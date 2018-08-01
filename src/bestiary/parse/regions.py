from .util import to_boolean
from .xml import TRANSLATION_STRINGS, region_definitions
from bestiary.models import Dungeon


def _region_valid_to_import(data):
    if 'unlock' in data:
        # Check that the unlock period is out of bounds of typical day/month numbers
        time_unit, unlock = data['unlock'].split(':')
        unlock = [int(val) for val in unlock.split(',')]
        if time_unit == 'Days':
            available = min(unlock) <= 7
        else:
            available = min(unlock) <= 12
    else:
        available = True

    return data['path'] != 'PVP' and to_boolean(data['inGame']) and available


def regions():
    for data in region_definitions():
        if _region_valid_to_import(data):
            try:
                dungeon = Dungeon.objects.get(game_id=data['sku'])
            except Dungeon.DoesNotExist:
                dungeon = Dungeon()
                dungeon.game_id = data['sku']

            dungeon.name = TRANSLATION_STRINGS[data['name']]
            if 'special_dungeon' in data['sku']:
                default_group = Dungeon.GROUP_ELEMENT
            else:
                default_group = Dungeon.GROUP_SCENARIO
            dungeon.group = data.get('group', default_group)

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
