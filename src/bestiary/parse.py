from glob import iglob
import xml.etree.ElementTree as ET

from .models import Creature


# Checking for XML strings to values
def to_boolean(string):
    if string in ['true', 'True', 'TRUE']:
        return True
    else:
        return False


TRANSLATION_STRINGS = {}
with open('bestiary/data_files/english.txt', encoding='utf8') as f:
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
    for file_path in iglob('bestiary/data_files/creaturesDefinitions*.xml'):
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            data = child.attrib

            try:
                c = Creature.objects.get(game_id=data['sku'])
            except Creature.DoesNotExist:
                c = Creature()
                c.game_id = data['sku']
                print(f'Creating new creature {c.game_id}')

            try:
                c.name = TRANSLATION_STRINGS[data['name']]
                c.playable = to_boolean(data['playable'])
                c.summonable = to_boolean(data['getInGatcha'])
                c.inMenagerie = to_boolean(data['inMenagerie'])
                c.rank = data['rank']
                c.archetype = data['class']
                c.element = data['element']
                c.group = data['group']
                c.subgroup = data['subgroup'].split(',')
                c.lore = TRANSLATION_STRINGS[data['lore']]
                c.hp = int(data['hp'])
                c.attack = int(data['attack'])
                c.defense = int(data['defense'])
                c.criticalChance = int(data['criticalChance'])
                c.criticalDamage = int(data['criticalDamage'])
                c.accuracy = float(data['accuracy'])
                c.resistance = float(data['resistance'])
                c.initialSpeed = float(data['initialSpeed'])
                c.speed = float(data['speed'])
                c.creatureType = data['creatureType']
                c.trackingName = data['trackingName']

                c.save()
            except (KeyError, ValueError) as e:
                print(f'Failed to create creature {data["sku"]}')
                print(type(e), e)
