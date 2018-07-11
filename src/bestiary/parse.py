import json
import os
import re
import xml.etree.ElementTree as ET
from glob import iglob

from django.conf import settings

from .models import Creature, Spell, SpellEffect, SpellUpgrade


# Checking for XML strings to values
def to_boolean(string):
    if string in ['true', 'True', 'TRUE']:
        return True
    else:
        return False


TRANSLATION_STRINGS = {}
with open(os.path.join(settings.BASE_DIR, 'bestiary/data_files/english.txt'), encoding='utf8') as f:
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


def creatures():
    for file_path in iglob(os.path.join(settings.BASE_DIR, 'bestiary/data_files/creaturesDefinitions*.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            data = child.attrib

            if data['sku'][-1] == 'b':
                # This is a secondary creature w/ alternate skill 1. Skip importing.
                # Alternate skills parsed in skills() function
                continue
            if data['element'] in ['Dark', 'Light']:
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


def evolutions():
    for file_path in iglob(os.path.join(settings.BASE_DIR, 'bestiary/data_files/creaturesDefinitions*.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            data = child.attrib

            if data['sku'][-1] == 'b':
                # This a secondary copy of a creature w/ alternate skills which are not imported.
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
                            c.evolvesTo = evolves_to
                            c.save()
                            break


def spells():
    # Parse spells for each creature
    for c in Creature.objects.all():
        # Get XML elements for this creature. May be multiple results.
        # These are the same creature with different spells
        creatures_data = _getcreaturedata(c.trackingName)
        if creatures_data is None:
            continue

        order = 0
        skus_used = []

        for slot in range(3):
            for creature_data in creatures_data:
                if f'spell{slot}' in creature_data:
                    sku = creature_data[f'spell{slot}']
                    if sku in skus_used:
                        # Identical spell on secondary creature data - no need to parse again
                        continue

                    try:
                        spell = Spell.objects.get(creature=c, game_id=sku)
                    except Spell.DoesNotExist:
                        spell = Spell()
                        spell.creature = c
                        spell.game_id = sku

                    spell.order = order
                    spell.slot = slot + 1
                    spell_data = _getspelldata(spell.game_id)
                    title_tid, desc_tid = creature_data[f'spell{slot}TIDS'].split(',')

                    spell.title = TRANSLATION_STRINGS[title_tid]
                    spell.description = TRANSLATION_STRINGS[desc_tid]
                    spell.image = creature_data.get(f'spell{slot}OverrideImage', '')
                    spell.type_image = spell_data.get('image', '')
                    spell.turns = spell_data.get('turns')
                    spell.passive = 'passive_spell' in spell.game_id
                    spell.passiveTrigger = spell_data.get('launch', '')
                    spell.save()
                    skus_used.append(sku)
                    order += 1

                    # Parse spell effects
                    effect_order = 0
                    if f'spell{slot}Params' in creature_data:
                        effect_params = creature_data[f'spell{slot}Params'].split(';')
                    else:
                        effect_params = []

                    for x in range(10):
                        if f'ingredient{x}' in spell_data:
                            try:
                                effect = SpellEffect.objects.get(spell=spell, order=x)
                            except SpellEffect.DoesNotExist:
                                effect = SpellEffect()
                                effect.spell = spell
                                effect.order = effect_order

                            effect.effect = spell_data[f'ingredient{x}']
                            effect.target = spell_data[f'ingredient{x}Target']

                            if x < len(effect_params):
                                effect.params = _paramstodict(effect_params[x])

                            if f'ingredient{x}Condition' in creature_data:
                                effect.condition = creature_data.get(f'ingredient{x}Condition', '').split(';')
                            else:
                                effect.condition = []

                            effect.save()
                            effect_order += 1
                        else:
                            break

                    # Parse random spell cast effects
                    # The effects from random spells should be added to this main spell
                    for effect in spell.spelleffect_set.filter(effect__in=['castRandomEnemy', 'castRandomAlly']):
                        # Get each spell ID from the random options and get its effects
                        for x in range(10):
                            if f'spell{x}' in effect.params['spell']:
                                rand_spell_data = _getspelldata(effect.params['spell'][f'spell{x}'])
                                rand_params = effect.params['spell'][f'spell{x}Params']

                                for eff_idx in range(10):
                                    if f'ingredient{eff_idx}' in rand_spell_data:
                                        try:
                                            rand_effect = SpellEffect.objects.get(spell=spell, order=effect_order)
                                        except SpellEffect.DoesNotExist:
                                            rand_effect = SpellEffect()
                                            rand_effect.spell = spell
                                            rand_effect.order = effect_order

                                        rand_effect.effect = rand_spell_data[f'ingredient{eff_idx}']
                                        rand_effect.target = rand_spell_data[f'ingredient{eff_idx}Target']
                                        rand_effect.params = _paramstodict(rand_params)
                                        rand_effect.probability = float(effect.params['spell'][f'spell{x}Prob'])
                                        rand_effect.save()
                                        effect_order += 1
                                    else:
                                        break
                            else:
                                # Delete any effect entries beyond what was parsed
                                SpellEffect.objects.filter(spell=spell, order__gte=effect_order).delete()
                                break

                    # Parse upgrades
                    if 'spellUpgradeSku' in spell_data:
                        upgrades = _getspellupgrades(spell_data['spellUpgradeSku'])
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

        # Remove spells assigned to this creature that were not processed
        c.spell_set.exclude(game_id__in=set(skus_used)).delete()


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


def _getcreaturedata(tracking_name):
    result = []
    # Return skill data for the sku provided
    for file_path in iglob(os.path.join(settings.BASE_DIR, 'bestiary/data_files/creaturesDefinitions*.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()
        result += root.findall(f'Definition[@trackingName="{tracking_name}"][@playable="true"]')

    if len(result):
        return [el.attrib for el in result]
    else:
        return None


def _getspelldata(sku):
    # Return skill data for the sku provided
    for file_path in iglob(os.path.join(settings.BASE_DIR, 'bestiary/data_files/creature*SpellsDefinitions.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()
        node = root.find(f'Definition[@sku="{sku}"]')
        if node is not None:
            return node.attrib


def _paramstodict(params):
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
        ret['spell'] = _getspellrandomdef(ret['spell'])

    return ret


skillUpMatcher = re.compile(r'^(?P<val>[-]?\d+),(?P<attribute>\w+):(?P<amount>[\d.]+)$')


def _getspellupgrades(sku):
    # Return upgrade data for the sku provided
    with open(os.path.join(settings.BASE_DIR, 'bestiary/data_files/creatureSpellIngredientUpgradesDefinitions.xml')) as f:
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


def _getspellrandomdef(sku):
    with open(os.path.join(settings.BASE_DIR, 'bestiary/data_files/creatureCastRandomSpellsDefinitions.xml')) as f:
        tree = ET.parse(f)
        root = tree.getroot()
        node = root.find(f'Definition[@sku="{sku}"]')

        return node.attrib