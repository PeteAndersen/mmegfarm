import os
import re
import xml.etree.ElementTree as ET
from glob import iglob

from django.conf import settings
from bestiary.models import Creature

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


# Creature files
def creature_definitions():
    result = []

    for file_path in iglob(os.path.join(DATA_DIR, 'creaturesDefinitions*.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            result.append(child.attrib)

    return result


def get_creature_data(sku):
    # Returns a single creature data
    for file_path in iglob(os.path.join(DATA_DIR, 'creaturesDefinitions*.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()
        node = root.find(f'Definition[@sku="{sku}"]')
        if node is not None:
            return node.attrib


def get_creature_data_by_trackingname(tracking_name):
    # Return matching creatures for the trackingName provided
    result = []

    for file_path in iglob(os.path.join(DATA_DIR, 'creaturesDefinitions*.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()
        result += root.findall(f'Definition[@trackingName="{tracking_name}"][@playable="true"]')

    if len(result):
        return [el.attrib for el in result]
    else:
        return None


def get_creatures_from_rewardpattern(pattern_sku):
    tree = ET.parse(os.path.join(DATA_DIR, 'patternRewardCreaturesDefinitions.xml'))
    root = tree.getroot()
    node = root.find(f'Definition[@sku="{pattern_sku}"]')
    if node is not None:
        # Creature skus are a comma separated list of skus
        creature_skus = node.attrib['creatures'].split(',')
        return Creature.objects.filter(game_id__in=creature_skus)


def get_spell_data(sku):
    # Return skill data for the sku provided
    for file_path in iglob(os.path.join(DATA_DIR, 'creature*SpellsDefinitions.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()
        node = root.find(f'Definition[@sku="{sku}"]')
        if node is not None:
            return node.attrib


skillUpMatcher = re.compile(r'^(?P<val>[-]?\d+),(?P<attribute>\w+):(?P<amount>[\d.]+)$')


def get_spell_upgrade_data(sku):
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


def get_spell_random_data(sku):
    with open(os.path.join(DATA_DIR, 'creatureCastRandomSpellsDefinitions.xml')) as f:
        tree = ET.parse(f)
        root = tree.getroot()
        node = root.find(f'Definition[@sku="{sku}"]')

        return node.attrib


# Regions, levels, enemies
def region_definitions():
    result = []

    for file_path in iglob(os.path.join(DATA_DIR, '*[rR]egionsDefinitions.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            result.append(child.attrib)

    return result


def level_definitions():
    result = []

    for file_path in [
        os.path.join(DATA_DIR, 'levelsDefinitions.xml'),
        os.path.join(DATA_DIR, 'specialDungeonLevelsDefinitions.xml')
    ]:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            result.append(child.attrib)

    return result


def get_difficulty_level(sku):
    for file_path in iglob(os.path.join(DATA_DIR, '*[lL]evelsDefinitions.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()
        node = root.find(f'Definition[@sku="{sku}"]')
        if node is not None:
            return node.attrib


def get_wave_definitions(difficulty_level_sku):
    results = []
    for file_path in iglob(os.path.join(DATA_DIR, '*[wW]avesDefinitions*.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()
        results += root.findall(f'Definition[@difficultyLevel="{difficulty_level_sku}"]')

    if len(results):
        return [el.attrib for el in results]
    else:
        return None


def get_boss_data(sku):
    tree = ET.parse(os.path.join(DATA_DIR, 'bossCreaturesDefinitions.xml'))
    root = tree.getroot()
    node = root.find(f'Definition[@sku="{sku}"]')
    if node is not None:
        return node.attrib


def get_rune_data_from_rewardpattern(sku):
    tree = ET.parse(os.path.join(DATA_DIR, 'patternRewardRunesDefinitions.xml'))
    root = tree.getroot()
    node = root.find(f'Definition[@sku="{sku}"]')
    if node is not None:
        return node.attrib


def get_rune_type_data(sku):
    tree = ET.parse(os.path.join(DATA_DIR, 'runeTypesDefinitions.xml'))
    root = tree.getroot()
    node = root.find(f'Definition[@sku="{sku}"]')
    if node is not None:
        return node.attrib


def get_rune_rarity_data(sku):
    tree = ET.parse(os.path.join(DATA_DIR, 'runeRaritiesDefinitions.xml'))
    root = tree.getroot()
    node = root.find(f'Definition[@sku="{sku}"]')
    if node is not None:
        return node.attrib


def get_rune_shape_data(sku):
    tree = ET.parse(os.path.join(DATA_DIR, 'runeShapesDefinitions.xml'))
    root = tree.getroot()
    node = root.find(f'Definition[@sku="{sku}"]')
    if node is not None:
        return node.attrib


def get_evolution_item(sku):
    tree = ET.parse(os.path.join(DATA_DIR, 'evolveItemsDefinitions.xml'))
    root = tree.getroot()
    node = root.find(f'Definition[@sku="{sku}"]')
    if node is not None:
        return node.attrib


def get_evolutionitem_data_from_rewardpattern(sku):
    tree = ET.parse(os.path.join(DATA_DIR, 'patternRewardEvolutionItemsDefinitions.xml'))
    root = tree.getroot()
    node = root.find(f'Definition[@sku="{sku}"]')
    if node is not None:
        return node.attrib
