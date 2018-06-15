from rest_framework import serializers

from bestiary.models import Creature, Spell, SpellUpgrade, SpellEffect, CreatureSpell


class SpellEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpellEffect
        fields = [
            'effect',
            'target',
            'condition',
            'permanent',
        ]


class SpellSerializer(serializers.ModelSerializer):
    effects = SpellEffectSerializer(source='spelleffect_set', many=True)
    class Meta:
        model = Spell
        exclude = [
            'id',
            'game_id',
        ]


class CreatureSpellSerializer(serializers.ModelSerializer):
    spell = SpellSerializer()

    class Meta:
        model = CreatureSpell
        fields = [
            'title',
            'description',
            'image',
            'params',
            'spell'
        ]


class CreatureSerializer(serializers.ModelSerializer):
    spells = CreatureSpellSerializer(source='creaturespell_set', many=True)

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
