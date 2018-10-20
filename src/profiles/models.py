import uuid

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.safestring import mark_safe

from bestiary.models import Creature, Dungeon, Level


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)


class CreatureInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game_id = models.IntegerField(null=True)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE)
    rank = models.IntegerField()
    level = models.IntegerField()


class GlyphInstance(models.Model):
    TYPE_VITALITY = 1
    TYPE_STRENGTH = 2
    TYPE_FRENZY = 3
    TYPE_DEFENSE = 4  # aka 'protection'
    TYPE_HASTE = 5
    TYPE_PRECSISION = 6
    TYPE_DESTRUCTION = 7
    TYPE_ENDURANCE = 8  # aka 'endurance'
    TYPE_LIFESTEAL = 9
    TYPE_APPEASEMENT = 10
    TYPE_MEDITATION = 11
    TYPE_IMMUNITY = 12

    TYPE_CHOICES = (
        (TYPE_VITALITY, 'Vitality'),
        (TYPE_STRENGTH, 'Strength'),
        (TYPE_FRENZY, 'Frenzy'),
        (TYPE_DEFENSE, 'Defense'),
        (TYPE_HASTE, 'Haste'),
        (TYPE_PRECSISION, 'Precision'),
        (TYPE_DESTRUCTION, 'Destruction'),
        (TYPE_ENDURANCE, 'Endurance'),
        (TYPE_LIFESTEAL, 'Life Steal'),
        (TYPE_APPEASEMENT, 'Appeasement'),
        (TYPE_MEDITATION, 'Meditation'),
        (TYPE_IMMUNITY, 'Immunity'),
    )

    RARITY_COMMON = 1
    RARITY_UNCOMMON = 2
    RARITY_RARE = 3
    RARITY_EPIC = 4
    RARITY_LEGENDARY = 5
    RARITY_DARK = 6

    RARITY_CHOICES = (
        (RARITY_COMMON, 'Common'),
        (RARITY_UNCOMMON, 'Uncommon'),
        (RARITY_RARE, 'Rare'),
        (RARITY_EPIC, 'Epic'),
        (RARITY_LEGENDARY, 'Legendary'),
        (RARITY_DARK, 'Dark'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game_id = models.IntegerField(null=True)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    creature = models.ForeignKey(CreatureInstance, on_delete=models.SET_NULL, null=True)
    type = models.IntegerField(choices=TYPE_CHOICES)
    rarity = models.IntegerField(choices=RARITY_CHOICES)
    stars = models.IntegerField()
    level = models.IntegerField()
    stats = JSONField(default=dict)


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    dungeon = models.ForeignKey(Dungeon, on_delete=models.SET_NULL, null=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)
    roster = models.ManyToManyField(CreatureInstance)
    description = models.TextField(
        null=True,
        blank=True,
        help_text=mark_safe(
            '<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'
        )
    )
