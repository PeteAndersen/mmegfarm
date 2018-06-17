import os
from glob import iglob
import xml.etree.ElementTree as ET
import re

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
                            spell = Spell.objects.get(creature=c, order=x)
                        except Spell.DoesNotExist:
                            spell = Spell()
                            spell.creature = c
                            spell.order = x

                        spell.game_id = data[f'spell{x}']
                        spell_data = _getspell(spell.game_id)
                        title_tid, desc_tid = data[f'spell{x}TIDS'].split(',')

                        spell.title = TRANSLATION_STRINGS[title_tid]
                        spell.description = TRANSLATION_STRINGS[desc_tid]
                        spell.image = data.get(f'spell{x}OverrideImage', '')
                        spell.type_image = spell_data.get('image', '')
                        spell.turns = spell_data.get('turns')
                        spell.passive = 'passive_spell' in spell.game_id
                        spell.passiveTrigger = spell_data.get('launch', '')
                        spell.save()

                        # Parse spell effects
                        if f'spell{x}Params' in data:
                            effectParams = data[f'spell{x}Params'].split(';')
                        else:
                            effectParams = []

                        for x in range(10):
                            if f'ingredient{x}' in spell_data:
                                try:
                                    effect = SpellEffect.objects.get(spell=spell, order=x)
                                except SpellEffect.DoesNotExist:
                                    effect = SpellEffect()
                                    effect.spell = spell
                                    effect.order = x

                                effect.effect = spell_data[f'ingredient{x}']
                                effect.target = spell_data[f'ingredient{x}Target']

                                if x < len(effectParams):
                                    effect.params = _paramstodict(effectParams[x])

                                if f'ingredient{x}Condition' in data:
                                    effect.condition = data.get(f'ingredient{x}Condition', '').split(';')
                                else:
                                    effect.condition = []

                                effect.save()
                            else:
                                # Delete any effect entries beyond what was parsed
                                SpellEffect.objects.filter(spell=spell, order__gt=x).delete()
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


def _getspell(sku):
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
            ret[values[0]] = values[1]
        else:
            # simply presence of key
            ret[values[0]] = True

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
                    upgrades.append({
                        'value': float(match.group('amount')),
                        'attribute': match.group('attribute'),
                        'description': TRANSLATION_STRINGS[data[f'skillUp{x}TID']],
                        'is_percentage': f'skillUp{x}Suffix' in data,
                    })
            else:
                break

        return upgrades
