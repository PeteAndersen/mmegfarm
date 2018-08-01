from bestiary.models import Dungeon, Level, Wave, Enemy, EnemySpell, EnemySpellEffect, Creature
from .rewards import get_rewards
from .spells import _fill_spell_data, _create_spell_effects
from .util import params_to_dict
from .xml import TRANSLATION_STRINGS, level_definitions, get_difficulty_level, get_wave_definitions, get_creature_data, \
    get_boss_data


def levels():
    for data in level_definitions():
        # This is a slow process so print to console to see progress
        print(f'Parsing level {data["sku"]}')

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

    difficulty_data = get_difficulty_level(data[_difficulty_keys[difficulty]])

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
        if 'rewards' in difficulty_data:
            level.rewards = get_rewards(difficulty_data['rewards'])
        if 'rewardsInstant' in difficulty_data:
            level.rewards_instant = get_rewards(difficulty_data['rewardsInstant'])

        level.save()

        # Parse waves
        waves_data = get_wave_definitions(difficulty_data['sku'])
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


def _create_wave_enemies(wave, enemies_string):
    valid_enemy_ids = []
    enemies_data = [
        params_to_dict(enemy_str) for enemy_str in enemies_string.split(';')
    ]

    for enemy_idx, enemy_data in enumerate(enemies_data):
        enemy = _create_enemy_creature(wave, enemy_idx, enemy_data)
        valid_enemy_ids.append(enemy.pk)

    # Delete other enemies assigned to this wave that were not in data files
    wave.enemy_set.exclude(pk__in=valid_enemy_ids).delete()


def _create_enemy_creature(wave, idx, params):
    # Enemies are instances of standard creatures with multipliers on stats
    try:
        enemy = Enemy.objects.get(wave=wave, order=idx)
    except Enemy.DoesNotExist:
        enemy = Enemy()
        enemy.wave = wave
        enemy.order = idx

    enemy.level = params.get('level', 1)
    enemy.rank = params.get('rank', 1)
    enemy.game_id = params['sku']

    # Get creature data
    if params['sku'].startswith('boss'):
        creature_data = get_boss_data(params['sku'])
    else:
        creature_data = get_creature_data(params['sku'])

    enemy.trackingName = creature_data.get('trackingName')
    enemy.name = TRANSLATION_STRINGS[creature_data['name']]
    enemy.archetype = creature_data['class']
    enemy.element = creature_data['element']

    if params['sku'].startswith('boss'):
        c = Creature.objects.filter(name=enemy.name, element=enemy.element).first()
        if c:
            enemy.trackingName = c.trackingName

        base_rank = int(creature_data['rank'])
        base_hp = int(creature_data['hp'])
        base_attack = int(creature_data['attack'])
        base_defense = int(creature_data['defense'])

        # Boss stats are taken directly from the creature_data and scaled
        enemy.hp = Enemy.get_hp(base_rank, base_hp, enemy.rank, enemy.level) * params.get('xHp', 1)
        enemy.attack = Enemy.get_attack(base_rank, base_attack, enemy.rank, enemy.level) * params.get('xAttack', 1)
        enemy.defense = Enemy.get_defense(base_rank, base_defense, enemy.rank, enemy.level) * params.get('xDefense', 1)
        enemy.speed = float(creature_data['speed']) * params.get('xSpeed', 1)
        enemy.initialSpeed = int(creature_data['initialSpeed'])
        enemy.criticalChance = round(float(creature_data['criticalChance']) * params.get('xCriticalChance', 1))
        enemy.criticalDamage = round(float(creature_data['criticalDamage']) * params.get('xCriticalDamage', 1))
        enemy.accuracy = float(creature_data['accuracy']) * params.get('xAccuracy', 1)  # Note - data key is a guess. Doesn't exist in data
        enemy.resistance = float(creature_data['resistance']) * params.get('xResistance', 1)  # Note - data key is a guess. Doesn't exist in data
    else:
        # Regular enemy stats are taken from the base creature,
        # scaled to appropriate rank/level, and then final scaling applied
        c = Creature.objects.get(game_id=params['sku'])
        enemy.hp = round(float(params.get('xHp', 1)) * c.get_hp(enemy.rank, enemy.level))
        enemy.attack = round(float(params.get('xAttack', 1)) * c.get_attack(enemy.rank, enemy.level))
        enemy.defense = round(float(params.get('xDefense', 1)) * c.get_defense(enemy.rank, enemy.level))
        enemy.speed = float(params.get('xSpeed', 1)) * c.speed
        enemy.initialSpeed = c.initialSpeed
        enemy.criticalChance = round(float(params.get('xCriticalChance', 1)) * c.criticalChance)
        enemy.criticalDamage = round(float(params.get('xCriticalDamage', 1)) * c.criticalDamage)
        enemy.accuracy = float(params.get('xAccuracy', 1)) * c.accuracy  # Note - xAccuracy key is a guess
        enemy.resistance = float(params.get('xResistance', 1)) * c.resistance  # Note - xResistance key is a guess

    enemy.boss_type = params.get('type')
    enemy.save()

    # Enemy spells
    spell_ids = []

    for slot in range(3):
        if f'spell{slot}' in creature_data:
            sku = creature_data[f'spell{slot}']

            try:
                spell = EnemySpell.objects.get(creature=enemy, slot=slot + 1)
            except EnemySpell.DoesNotExist:
                spell = EnemySpell()
                spell.creature = enemy

            spell.game_id = sku
            spell = _fill_spell_data(spell, creature_data, slot)
            spell_ids.append(spell.pk)

            _create_spell_effects(spell, creature_data, effect_model=EnemySpellEffect)

    # Remove spells assigned to this creature that were not processed
    enemy.enemyspell_set.exclude(pk__in=set(spell_ids)).delete()

    return enemy
