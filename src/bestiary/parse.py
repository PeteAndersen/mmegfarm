import os
from glob import iglob
import xml.etree.ElementTree as ET
import re

from django.conf import settings

from .models import Creature, Spell, CreatureSpell, SpellEffect, SpellUpgrade


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
            print(data['sku'])

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
                print(f'Unable to save {data["sku"]}. {type(e)}: {e}')
            else:
                # Parse spells
                for x in range(3):
                    if f'spell{x}' in data:
                        try:
                            s = Spell.objects.get(game_id=data[f'spell{x}'])
                        except Spell.DoesNotExist:
                            raise ValueError("Tried to get a spell that doesn't exist yet. Do you need to parse spells first?")
                        else:
                            try:
                                cspell = CreatureSpell.objects.get(creature=c, spell=s, order=x)
                            except CreatureSpell.DoesNotExist:
                                cspell = CreatureSpell()
                                cspell.creature = c
                                cspell.spell = s
                                cspell.order = x

                            title_tid, desc_tid = data[f'spell{x}TIDS'].split(',')
                            cspell.title = TRANSLATION_STRINGS[title_tid]
                            cspell.description = TRANSLATION_STRINGS[desc_tid]
                            cspell.image = data.get(f'spell{x}OverrideImage', '')
                            cspell.params = data.get(f'spell{x}Params', '')
                            cspell.save()


def spells():
    for file_path in iglob(os.path.join(settings.BASE_DIR, 'bestiary/data_files/creature*SpellsDefinitions.xml')):
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            data = child.attrib

            try:
                s = Spell.objects.get(game_id=data['sku'])
            except Spell.DoesNotExist:
                s = Spell()
                s.game_id = data['sku']

            try:
                s.image = data.get('image', '')
                s.turns = int(data['turns']) if 'turns' in data else None
                s.save()

                # Parse effects
                for x in range(10):
                    if f'ingredient{x}' in data:
                        try:
                            effect = SpellEffect.objects.get(spell=s, order=x)
                        except SpellEffect.DoesNotExist:
                            effect = SpellEffect()
                            effect.spell = s
                            effect.order = x

                        effect.effect = data[f'ingredient{x}']
                        effect.target = data[f'ingredient{x}Target']
                        effect.condition = data.get(f'ingredient{x}Condition', '').split(';')
                        effect.save()
                    else:
                        # Delete any effect entries beyond what was parsed
                        SpellEffect.objects.filter(spell=s, order__gt=x).delete()
                        break

                # Parse upgrades
                if 'spellUpgradeSku' in data:
                    upgrades = spellupgrade(data['spellUpgradeSku'])
                    for x, upgrade_data in enumerate(upgrades):
                        try:
                            upgrade = SpellUpgrade.objects.get(spell=s, order=x)
                        except SpellUpgrade.DoesNotExist:
                            upgrade = SpellUpgrade()
                            upgrade.spell = s
                            upgrade.order = x

                        upgrade.game_id = data['spellUpgradeSku']
                        upgrade.amount = upgrade_data['value']
                        upgrade.is_percentage = upgrade_data['is_percentage']
                        upgrade.attribute = upgrade_data['attribute']
                        upgrade.description = upgrade_data['description']
                        upgrade.save()

                    # Delete any upgrade entries beyond what was parsed
                    SpellUpgrade.objects.filter(spell=s, order__gte=len(upgrades)).delete()

            except (KeyError, ValueError) as e:
                print(f'Unable to save {data["sku"]}. {type(e)}: {e}')


skillUpMatcher = re.compile(r'^(?P<val>[-]?\d+),(?P<attribute>\w+):(?P<amount>[\d.]+)$')


def spellupgrade(sku):
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
                    upgrades.append({
                        'value': float(match.group('amount')),
                        'attribute': match.group('attribute'),
                        'description': TRANSLATION_STRINGS[data[f'skillUp{x}TID']],
                        'is_percentage': f'skillUp{x}Suffix' in data,
                    })
            else:
                break

        return upgrades
