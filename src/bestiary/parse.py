import json
import os
import re
import xml.etree.ElementTree as ET
from glob import iglob

from django.conf import settings

from .models import Creature, Spell, SpellEffect, SpellUpgrade, Dungeon, Level, Wave, Enemy, Boss, BossSpell, BossSpellEffect


# string true/false to bool
def to_boolean(string):
    if string in ['true', 'True', 'TRUE']:
        return True
    else:
        return False


DATA_DIR = os.path.join(settings.BASE_DIR, 'bestiary/data_files')
TRANSLATION_STRINGS = {}
with open(os.path.join(DATA_DIR, 'english.txt'), encoding='utf8') as f:
    last_key = None

    for line in f:
        if line.startswith('TID_'):
            # New string definition
            key, text = line.split('=', 1)
            TRANSLATION_STRINGS[key] = text.strip()
            last_key = key
        else:
            # Continuing string definition that contains line breaks
            TRANSLATION_STRINGS[last_key] += f'\n{line}'


# CREATURES AND SPELLS
def creatures():
    for file_path in iglob(os.path.join(DATA_DIR, 'creaturesDefinitions*.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            data = child.attrib

            if data['element'] in ['dark', 'light']:
                # Skip L/D elements because their data is incomplete
                continue

            try:
                c = Creature.objects.get(game_id=data['sku'])
            except Creature.DoesNotExist:
                c = Creature()
                c.game_id = data['sku']
            try:
                c.name = TRANSLATION_STRINGS[data['name']]
                c.playable = to_boolean(data['playable'])
                c.summonable = to_boolean(data['getInGatcha'])
                c.inMenagerie = to_boolean(data['inMenagerie'])
                c.rank = int(data['rank'])
                c.archetype = data['class']
                c.element = data['element']
                c.group = data['group']
                c.subgroup = data['subgroup'].split(',')
                c.lore = TRANSLATION_STRINGS[data['lore']]
                c.creatureType = data['creatureType']
                c.trackingName = data['trackingName']

                c.hp = int(data['hp'])
                c.attack = int(data['attack'])
                c.defense = int(data['defense'])
                c.criticalChance = int(data['criticalChance'])
                c.criticalDamage = int(data['criticalDamage'])
                c.accuracy = float(data['accuracy'])
                c.resistance = float(data['resistance'])
                c.initialSpeed = float(data['initialSpeed'])
                c.speed = float(data['speed'])

                c.evoHp = int(data.get('evoStatHP', 0))
                c.evoAttack = int(data.get('evoStatAttack', 0))
                c.evoDefense = int(data.get('evoStatDefense', 0))
                c.evoCriticalChance = int(data.get('evoStatCriticalChance', 0))

                c.save()
            except (KeyError, ValueError) as e:
                print(f'Unable to save {data["sku"]}. {type(e)}: {e}')

    # Final step - make sure any new creatures have a slug
    for c in Creature.objects.filter(slug__isnull=True):
        c.save()


def evolutions():
    for file_path in iglob(os.path.join(DATA_DIR, 'creaturesDefinitions*.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            data = child.attrib

            if data['element'] in ['dark', 'light']:
                continue

            try:
                c = Creature.objects.get(game_id=data['sku'])
            except Creature.DoesNotExist:
                print(f'Could not find {data["sku"]} in creature database. Skipping.')
            else:
                if 'evolvesTo' in data:
                    for evo_data in data['evolvesTo'].split(';'):
                        if ',' in evo_data:
                            # Can evolve to more than 1 creature
                            game_id, _ = evo_data.split(',')
                        else:
                            game_id = evo_data

                        try:
                            evolves_to = Creature.objects.get(game_id=game_id)
                        except Creature.DoesNotExist:
                            # Try the other game ID in the evolvesTo field
                            continue
                        else:
                            evolves_to.evolvesFrom = c
                            evolves_to.save()


def spells():
    # Parse spells for each creature
    for c in Creature.objects.all():
        skus_used = []
        # Get XML elements for this creature. May be multiple results.
        # These are the same creature with different spells
        creature_data = _get_creature_data(c.game_id)

        for slot in range(3):
            if f'spell{slot}' in creature_data:
                sku = creature_data[f'spell{slot}']

                try:
                    spell = Spell.objects.get(creature=c, game_id=sku)
                except Spell.DoesNotExist:
                    spell = Spell()
                    spell.creature = c
                    spell.game_id = sku

                spell = _fill_spell_data(spell, creature_data, slot)
                spell.save()
                skus_used.append(spell)

                _create_spell_effects(spell, creature_data)
                _create_spell_upgrades(spell)

        # Remove spells assigned to this creature that were not processed
        c.spell_set.exclude(game_id__in=set(skus_used)).delete()


def _fill_spell_data(spell, creature_data, slot):
    spell.slot = slot + 1
    spell_data = _get_spell_data(spell.game_id)
    title_tid, desc_tid = creature_data[f'spell{slot}TIDS'].split(',')

    spell.title = TRANSLATION_STRINGS[title_tid]
    spell.description = TRANSLATION_STRINGS[desc_tid]
    spell.image = creature_data.get(f'spell{slot}OverrideImage', '')
    spell.type_image = spell_data.get('image', '')
    spell.turns = spell_data.get('turns')
    spell.passive = 'passive_spell' in spell.game_id
    spell.passiveTrigger = spell_data.get('launch', '')
    spell.save()

    return spell


def _create_spell_effects(spell, creature_data, *args, **kwargs):
    effect_model = kwargs.get('effect_model', SpellEffect)

    # Parse spell effects
    spell_data = _get_spell_data(spell.game_id)
    effect_order = 0

    if f'spell{spell.slot - 1}Params' in creature_data:
        effect_params = creature_data[f'spell{spell.slot - 1}Params'].split(';')
    else:
        effect_params = []

    for x in range(10):
        if f'ingredient{x}' in spell_data:
            try:
                effect = effect_model.objects.get(spell=spell, order=x)
            except effect_model.DoesNotExist:
                effect = effect_model()
                effect.spell = spell
                effect.order = effect_order

            effect.effect = spell_data[f'ingredient{x}']
            effect.target = spell_data[f'ingredient{x}Target']

            if x < len(effect_params):
                effect.params = _params_to_dict(effect_params[x])

            if f'ingredient{x}Condition' in spell_data:
                effect.condition = spell_data[f'ingredient{x}Condition'].split(';')

            effect.save()
            effect_order += 1
        else:
            break

    # Parse random spell cast effects
    # The effects from random spells should be added to this main spell
    for effect in effect_model.objects.filter(spell=spell, effect__in=['castRandomEnemy', 'castRandomAlly']):
        # Get each spell ID from the random options and get its effects
        for x in range(10):
            if f'spell{x}' in effect.params['spell']:
                rand_spell_data = _get_spell_data(effect.params['spell'][f'spell{x}'])
                rand_params = effect.params['spell'][f'spell{x}Params'].split(';')

                for eff_idx in range(10):
                    if f'ingredient{eff_idx}' in rand_spell_data:
                        try:
                            rand_effect = effect_model.objects.get(spell=spell, order=effect_order)
                        except effect_model.DoesNotExist:
                            rand_effect = effect_model()
                            rand_effect.spell = spell
                            rand_effect.order = effect_order

                        rand_effect.effect = rand_spell_data[f'ingredient{eff_idx}']
                        rand_effect.target = rand_spell_data[f'ingredient{eff_idx}Target']
                        rand_effect.params = _params_to_dict(rand_params[eff_idx])
                        rand_effect.probability = float(effect.params['spell'][f'spell{x}Prob'])
                        if f'ingredient{eff_idx}Condition' in rand_spell_data:
                            rand_effect.condition = rand_spell_data[f'ingredient{eff_idx}Condition'].split(';')
                        rand_effect.save()
                        effect_order += 1
                    else:
                        break
            else:
                break
    # Delete any effect entries beyond what was parsed
    effect_model.objects.filter(spell=spell, order__gte=effect_order).delete()


def _create_spell_upgrades(spell):
    # Parse upgrades
    spell_data = _get_spell_data(spell.game_id)

    if 'spellUpgradeSku' in spell_data:
        upgrades = _get_spell_upgrades(spell_data['spellUpgradeSku'])
        for x, upgrade_data in enumerate(upgrades):
            try:
                upgrade = SpellUpgrade.objects.get(spell=spell, order=x)
            except SpellUpgrade.DoesNotExist:
                upgrade = SpellUpgrade()
                upgrade.spell = spell
                upgrade.order = x

            upgrade.game_id = spell_data['spellUpgradeSku']
            upgrade.amount = upgrade_data['value']
            upgrade.is_percentage = upgrade_data['is_percentage']
            upgrade.attribute = upgrade_data['attribute']
            upgrade.description = upgrade_data['description']
            upgrade.save()

        # Delete any upgrade entries beyond what was parsed
        SpellUpgrade.objects.filter(spell=spell, order__gte=len(upgrades)).delete()


def effects():
    tree = ET.parse('bestiary/data_files/spellIconsDefinitions.xml')
    root = tree.getroot()

    return {
        child.attrib['spell']: {
            'sku': child.attrib['sku'],
            'spell': child.attrib['spell'],
            'icon': child.attrib['icon'],
            'is_buff': child.attrib['buff'],
            'title': TRANSLATION_STRINGS[child.attrib['tidTitle']],
            'description': TRANSLATION_STRINGS[child.attrib['tidDesc']]
        } for child in root
    }


def _get_creature_data(sku):
    # Return skill data for the sku provided
    for file_path in iglob(os.path.join(DATA_DIR, 'creaturesDefinitions*.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()
        node = root.find(f'Definition[@sku="{sku}"]')
        if node is not None:
            return node.attrib


def _get_spell_data(sku):
    # Return skill data for the sku provided
    for file_path in iglob(os.path.join(DATA_DIR, 'creature*SpellsDefinitions.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()
        node = root.find(f'Definition[@sku="{sku}"]')
        if node is not None:
            return node.attrib


def _params_to_dict(params):
    ret = {}
    for param in params.split(','):
        values = param.split(':')
        if len(values) == 2:
            # key:value pair
            try:
                # See if it's an int or float by parsing it
                value = json.loads(values[1])
                ret[values[0]] = value
            except json.JSONDecodeError:
                # Just interpret as string
                ret[values[0]] = values[1]
        else:
            # simply presence of key
            ret[values[0]] = True

    if 'spell' in ret:
        ret['spell'] = _get_spell_random_def(ret['spell'])

    return ret


skillUpMatcher = re.compile(r'^(?P<val>[-]?\d+),(?P<attribute>\w+):(?P<amount>[\d.]+)$')


def _get_spell_upgrades(sku):
    # Return upgrade data for the sku provided
    with open(os.path.join(DATA_DIR, 'creatureSpellIngredientUpgradesDefinitions.xml')) as f:
        tree = ET.parse(f)
        root = tree.getroot()
        node = root.find(f'Definition[@sku="{sku}"]')

        upgrades = []
        data = node.attrib

        for x in range(10):
            if f'skillUp{x}' in data:
                match = skillUpMatcher.match(data[f'skillUp{x}'])

                if match:
                    if match.group('attribute') == 'turns' and float(match.group('val')) != 0:
                        val = float(match.group('val'))
                    else:
                        val = float(match.group('amount'))

                    upgrades.append({
                        'value': val,
                        'attribute': match.group('attribute'),
                        'description': TRANSLATION_STRINGS[data[f'skillUp{x}TID']],
                        'is_percentage': f'skillUp{x}Suffix' in data,
                    })
            else:
                break

        return upgrades


def _get_spell_random_def(sku):
    with open(os.path.join(DATA_DIR, 'creatureCastRandomSpellsDefinitions.xml')) as f:
        tree = ET.parse(f)
        root = tree.getroot()
        node = root.find(f'Definition[@sku="{sku}"]')

        return node.attrib


# DUNGEONS, ENEMIES, AND REWARDS
def regions():
    for file_path in iglob(os.path.join(DATA_DIR, '*[rR]egionsDefinitions.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            data = child.attrib

            if data['path'] != 'PVP' and to_boolean(data['inGame']):
                try:
                    dungeon = Dungeon.objects.get(game_id=data['sku'])
                except Dungeon.DoesNotExist:
                    dungeon = Dungeon()
                    dungeon.game_id = data['sku']

                dungeon.name = TRANSLATION_STRINGS[data['name']]
                dungeon.group = data.get('group', Dungeon.GROUP_SCENARIO)

                if 'unlock' in data:
                    # Dungeon is only open certain days or months
                    time_unit, unlock = data['unlock'].split(':')
                    unlock = [int(val) for val in unlock.split(',')]
                    unlock.sort()

                    if time_unit == 'Days':
                        dungeon.days_available = unlock
                        dungeon.always_available = len(unlock) == 7
                    if time_unit == 'Months':
                        dungeon.months_available = unlock
                        dungeon.always_available = len(unlock) == 12
                else:
                    dungeon.always_available = True

                dungeon.save()


def levels():
    for file_path in [
        os.path.join(DATA_DIR, 'levelsDefinitions.xml'),
        os.path.join(DATA_DIR, 'specialDungeonLevelsDefinitions.xml')
    ]:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            data = child.attrib

            # Scenarios have easy, medium, hard
            if 'easyLevel' in data:
                _create_level(data, Level.DIFFICULTY_EASY)
            if 'mediumLevel' in data:
                _create_level(data, Level.DIFFICULTY_MEDIUM)
            if 'hardLevel' in data:
                _create_level(data, Level.DIFFICULTY_HARD)
            if 'level' in data:
                # Special dungeons
                _create_level(data, None)


_difficulty_keys = {
    Level.DIFFICULTY_EASY: 'easyLevel',
    Level.DIFFICULTY_MEDIUM: 'mediumLevel',
    Level.DIFFICULTY_HARD: 'hardLevel',
    None: 'level',
}


def _create_level(data, difficulty):
    try:
        level = Level.objects.get(game_id=data['sku'], difficulty=difficulty)
    except Level.DoesNotExist:
        level = Level()
        level.game_id = data['sku']
        level.difficulty = difficulty

    difficulty_data = _get_difficulty_level(data[_difficulty_keys[difficulty]])

    try:
        dungeon = Dungeon.objects.get(game_id=data['region'])
    except Dungeon.DoesNotExist:
        print(f'Could not find region {data["region"]} for level {data["sku"]}. Skipping')
        return
    else:
        level.dungeon = dungeon
        level.order = int(data['order'])

        level.slots = int(difficulty_data['allies'])
        level.energy_cost = int(difficulty_data['energy'])
        level.save()

        # TODO: Parse rewards here?

        # Parse waves
        waves_data = _get_waves(difficulty_data['sku'])
        wave_skus = []
        if len(waves_data):
            for wave_idx, wave_data in enumerate(waves_data):
                try:
                    wave = Wave.objects.get(game_id=wave_data['sku'])
                except Wave.DoesNotExist:
                    wave = Wave()
                    wave.game_id = wave_data['sku']

                wave.level = level
                wave.order = wave_idx
                wave.save()
                wave_skus.append(wave_data['sku'])
                _create_wave_enemies(wave, wave_data['enemies'])

            # Delete any other waves related to this level that were not in data files
            level.wave_set.exclude(game_id__in=wave_skus).delete()

        else:
            print(f'No waves found for level {data["sku"]}!')


def _get_difficulty_level(sku):
    for file_path in iglob(os.path.join(DATA_DIR, '*[lL]evelsDefinitions.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()
        node = root.find(f'Definition[@sku="{sku}"]')
        if node is not None:
            return node.attrib


def _get_waves(difficulty_level_sku):
    results = []
    for file_path in iglob(os.path.join(DATA_DIR, '*[wW]avesDefinitions*.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()
        results += root.findall(f'Definition[@difficultyLevel="{difficulty_level_sku}"]')

    if len(results):
        return [el.attrib for el in results]
    else:
        return None


def _create_wave_enemies(wave, enemies_string):
    valid_enemy_ids = []
    valid_boss_ids = []
    enemies_data = [
        _params_to_dict(enemy_str) for enemy_str in enemies_string.split(';')
    ]

    for enemy_idx, enemy_data in enumerate(enemies_data):
        if enemy_data['sku'].startswith('boss'):
            enemy = _create_boss_enemy(wave, enemy_idx, enemy_data)
            valid_boss_ids.append(enemy.pk)
        else:
            enemy = _create_trash_enemy(wave, enemy_idx, enemy_data)
            valid_enemy_ids.append(enemy.pk)

    # Delete other enemies assigned to this wave that were not in data files
    wave.enemy_set.exclude(pk__in=valid_enemy_ids).delete()
    wave.boss_set.exclude(pk__in=valid_boss_ids).delete()


def _create_trash_enemy(wave, idx, data):
    # Trash enemies are instances of standard creatures with multipliers on stats

    try:
        enemy = Enemy.objects.get(wave=wave, order=idx)
    except Enemy.DoesNotExist:
        enemy = Enemy()
        enemy.wave = wave
        enemy.order = idx

    enemy.creature = Creature.objects.get(game_id=data['sku'])
    enemy.level = data.get('level', 1)
    enemy.rank = data.get('rank', 1)
    enemy.hpMulti = data.get('xHp', 1)
    enemy.attackMulti = data.get('xAttack', 1)
    enemy.defenseMulti = data.get('xDefense', 1)
    enemy.speedMulti = data.get('xSpeed', 1)
    enemy.criticalChanceMulti = data.get('xCriticalChance', 1)
    enemy.criticalDamageMulti = data.get('xCriticalDamage', 1)
    enemy.accuracyMulti = data.get('xAccuracy', 1)  # Note - data key is a guess. Doesn't exist in data
    enemy.resistanceMulti = data.get('xResistance', 1)  # Note - data key is a guess. Doesn't exist in data
    enemy.miniboss = data.get('type') == 'miniBoss'
    enemy.save()

    return enemy


def _create_boss_enemy(wave, idx, boss_params):
    # Boss enemies are unique creatures
    try:
        boss = Boss.objects.get(wave=wave, order=idx)
    except Boss.DoesNotExist:
        boss = Boss()
        boss.wave = wave
        boss.order = idx

    boss_data = _get_boss_data(boss_params['sku'])

    boss.game_id = boss_params['sku']
    boss.playable = to_boolean(boss_data['playable'])
    boss.name = TRANSLATION_STRINGS[boss_data['name']]
    boss.rank = int(boss_params.get('rank', boss_data['rank']))
    boss.level = int(boss_params['level'])
    boss.archetype = boss_data['class']
    boss.element = boss_data['element']

    # Get trackingName from creature match (if one exists)
    c = Creature.objects.filter(name=boss.name, element=boss.element).first()
    if c:
        boss.trackingName = c.trackingName

    boss.hp = float(boss_data['hp']) * boss_params.get('xHp', 1)
    boss.attack = float(boss_data['attack']) * boss_params.get('xAttack', 1)
    boss.defense = float(boss_data['defense']) * boss_params.get('xDefense', 1)
    boss.speed = float(boss_data['speed']) * boss_params.get('xSpeed', 1)
    boss.initialSpeed = int(boss_data['initialSpeed'])
    boss.criticalChance = float(boss_data['speed']) * boss_params.get('xCriticalChance', 1)
    boss.criticalDamage = float(boss_data['speed']) * boss_params.get('xCriticalDamage', 1)
    boss.accuracy = float(boss_data['speed']) * boss_params.get('xAccuracy', 1)  # Note - data key is a guess. Doesn't exist in data
    boss.resistance = float(boss_data['speed']) * boss_params.get('xResistance', 1)  # Note - data key is a guess. Doesn't exist in data

    boss.save()

    # Boss spells
    skus_used = []
    for slot in range(3):
        if f'spell{slot}' in boss_data:
            sku = boss_data[f'spell{slot}']

            try:
                spell = BossSpell.objects.get(creature=boss, game_id=sku)
            except BossSpell.DoesNotExist:
                spell = BossSpell()
                spell.creature = boss
                spell.game_id = sku

            spell = _fill_spell_data(spell, boss_data, slot)
            spell.save()
            skus_used.append(spell)

            _create_spell_effects(spell, boss_data, effect_model=BossSpellEffect)

    # Remove spells assigned to this creature that were not processed
    boss.bossspell_set.exclude(game_id__in=set(skus_used)).delete()

    return boss


def _get_boss_data(sku):
    tree = ET.parse(os.path.join(DATA_DIR, 'bossCreaturesDefinitions.xml'))
    root = tree.getroot()
    node = root.find(f'Definition[@sku="{sku}"]')
    if node is not None:
        return node.attrib
