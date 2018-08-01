
from bestiary.models import Creature, Spell, SpellEffect, SpellUpgrade
from .xml import get_creature_data_by_trackingname, get_spell_data, get_spell_upgrade_data, TRANSLATION_STRINGS
from .util import params_to_dict


def spells():
    # Parse spells for each creature
    for c in Creature.objects.all():
        skus_used = []
        # Get XML elements for this creature. May be multiple results.
        # These are the same creature with different spells
        creatures_data = get_creature_data_by_trackingname(c.trackingName)
        if creatures_data is None:
            continue

        order = 0

        for slot in range(3):
            for creature_data in creatures_data:
                if f'spell{slot}' in creature_data:
                    sku = creature_data[f'spell{slot}']

                    if sku in skus_used:
                        # Identical spell on secondary creature data - no need to parse again
                        continue

                    try:
                        spell = Spell.objects.get(creature=c, order=order)
                    except Spell.DoesNotExist:
                        spell = Spell()
                        spell.creature = c
                        spell.order = order

                    spell.game_id = sku
                    spell = _fill_spell_data(spell, creature_data, slot)
                    skus_used.append(sku)
                    order += 1

                    _create_spell_effects(spell, creature_data)
                    _create_spell_upgrades(spell)

        # Remove spells assigned to this creature that were not processed
        c.spell_set.filter(order__gte=order).delete()


def _fill_spell_data(spell, creature_data, slot):
    spell.slot = slot + 1
    spell_data = get_spell_data(spell.game_id)
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
    spell_data = get_spell_data(spell.game_id)
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
                effect.params = params_to_dict(effect_params[x])

            if f'ingredient{x}Condition' in spell_data:
                effect.condition = spell_data[f'ingredient{x}Condition'].split(';')

            effect.save()
            effect_order += 1
        else:
            break

    # Delete any effect entries beyond this point to avoid parsing old random effects.
    effect_model.objects.filter(spell=spell, order__gte=effect_order).delete()

    # Parse random spell cast effects
    # The effects from random spells should be added to this main spell
    for effect in effect_model.objects.filter(spell=spell, effect__in=['castRandomEnemy', 'castRandomAlly']):
        # Get each spell ID from the random options and get its effects
        for x in range(10):
            if f'spell{x}' in effect.params['spell']:
                rand_spell_data = get_spell_data(effect.params['spell'][f'spell{x}'])
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
                        rand_effect.params = params_to_dict(rand_params[eff_idx])
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
    spell_data = get_spell_data(spell.game_id)

    if 'spellUpgradeSku' in spell_data:
        upgrades = get_spell_upgrade_data(spell_data['spellUpgradeSku'])
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
