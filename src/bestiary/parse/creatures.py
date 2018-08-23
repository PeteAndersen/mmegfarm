from django.db.models import Count

from bestiary.models import Creature
from .util import to_boolean
from .xml import TRANSLATION_STRINGS, creature_definitions


def creatures():
    for data in creature_definitions():
        if data['element'] in ['dark', 'light']:
            # Skip L/D elements because their data is incomplete
            continue

        if data['sku'][-1] == 'b':
            # This is a secondary creature w/ alternate skill 1. Skip importing.
            # Alternate skills parsed in skills() function
            continue

        if data['status'] == 'disabled':
            # Data exists but not in game yet
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
    for data in creature_definitions():
        if data['element'] in ['dark', 'light']:
            continue

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
                        evolves_to.evolvesFrom = c
                        evolves_to.save()


def special_case_creatures():
    # Tawerets all have the same name for creatureType. Need to update evolved ones.
    Creature.objects.annotate(
        evolvesTo__count=Count('evolvesTo')
    ).filter(
        name__icontains="taweret", evolvesTo__count=0
    ).update(
        creatureType='creature_type_taweret_elite'
    )
