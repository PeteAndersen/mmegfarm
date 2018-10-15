from rest_framework import serializers

from .models import Creature, Spell, SpellUpgrade, SpellEffect, Dungeon, Level, Wave, Enemy, EnemySpell, \
    EnemySpellEffect


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


class EnemySpellEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnemySpellEffect
        fields = [
            'effect',
            'target',
            'params',
            'condition',
            'permanent',
            'probability',
        ]


class EnemySpellSerializer(serializers.ModelSerializer):
    effects = EnemySpellEffectSerializer(source='enemyspelleffect_set', many=True)

    class Meta:
        model = EnemySpell
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
            'effects',
        ]


class EnemySerializer(serializers.ModelSerializer):
    spells = EnemySpellSerializer(source='enemyspell_set', many=True)

    class Meta:
        model = Enemy
        fields = [
            'id',
            'name',
            'rank',
            'level',
            'archetype',
            'element',
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
            'boss_type',
            'spells',
        ]


class WaveSerializer(serializers.ModelSerializer):
    enemies = EnemySerializer(source='enemy_set', many=True, read_only=True)

    class Meta:
        model = Wave
        fields = [
            'id',
            'level',
            'enemies',
        ]


class LevelSerializer(serializers.ModelSerializer):
    difficulty = serializers.CharField(source='get_difficulty_display')
    waves = serializers.PrimaryKeyRelatedField(source='wave_set', many=True, read_only=True)

    class Meta:
        model = Level
        fields = [
            'id',
            'game_id',
            'dungeon',
            'difficulty',
            'slots',
            'energy_cost',
            'waves',
            'rewards',
            'rewards_instant',
        ]


class DungeonSerializer(serializers.ModelSerializer):
    levels = serializers.PrimaryKeyRelatedField(source='level_set', many=True, read_only=True)

    class Meta:
        model = Dungeon
        fields = [
            'id',
            'name',
            'group',
            'always_available',
            'days_available',
            'months_available',
            'levels',
        ]