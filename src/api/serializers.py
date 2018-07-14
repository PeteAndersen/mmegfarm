from rest_framework import serializers

from bestiary.models import Creature, Spell, SpellUpgrade, SpellEffect, Dungeon, Level, Wave, Enemy


class SpellEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpellEffect
        fields = [
            'effect',
            'target',
            'params',
            'condition',
            'permanent',
            'probability',
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
            'slot',
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
            'id',
            'slug',
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
            'evolvesTo',
            'evolvesFrom',
            'hp',
            'attack',
            'defense',
            'maxLvlHp',
            'maxLvlAttack',
            'maxLvlDefense',
            'criticalChance',
            'criticalDamage',
            'accuracy',
            'resistance',
            'evoHp',
            'evoAttack',
            'evoDefense',
            'initialSpeed',
            'speed',
            'spells',
        ]


class EnemySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enemy
        fields = '__all__'


class WaveSerializer(serializers.ModelSerializer):
    enemies = EnemySerializer(source='enemy_set', many=True, read_only=True)

    class Meta:
        model = Wave
        fields = '__all__'


class LevelSerializer(serializers.ModelSerializer):
    waves = WaveSerializer(source='wave_set', many=True, read_only=True)

    class Meta:
        model = Level
        fields = [
            'id',
            'game_id',
            'order',
            'difficulty',
            'slots',
            'energy_cost',
            'waves',
        ]


class DungeonSerializer(serializers.ModelSerializer):
    levels = LevelSerializer(source='level_set', many=True, read_only=True)

    class Meta:
        model = Dungeon
        fields = [
            'id',
            'game_id',
            'name',
            'group',
            'always_available',
            'days_available',
            'months_available',
            'levels',
        ]
