from rest_framework import serializers

from bestiary.models import Creature, Spell, SpellUpgrade, SpellEffect


class SpellEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpellEffect
        fields = [
            'effect',
            'target',
            'params',
            'condition',
            'permanent',
        ]


class SpellUpgradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpellUpgrade
        fields = [
            'amount',
            'is_percentage',
            'attribute',
            'description',
        ]


class SpellSerializer(serializers.ModelSerializer):
    effects = SpellEffectSerializer(source='spelleffect_set', many=True)
    upgrades = SpellUpgradeSerializer(source='spellupgrade_set', many=True)

    class Meta:
        model = Spell
        fields = [
            'id',
            'title',
            'description',
            'image',
            'type_image',
            'turns',
            'passive',
            'passiveTrigger',
            'upgrades',
            'effects',
        ]


class CreatureSerializer(serializers.ModelSerializer):
    spells = SpellSerializer(source='spell_set', many=True)

    class Meta:
        model = Creature
        fields = [
            'name',
            'playable',
            'summonable',
            'inMenagerie',
            'rank',
            'archetype',
            'element',
            'group',
            'subgroup',
            'lore',
            'creatureType',
            'trackingName',
            'hp',
            'attack',
            'defense',
            'criticalChance',
            'criticalDamage',
            'accuracy',
            'resistance',
            'initialSpeed',
            'speed',
            'spells',
        ]
