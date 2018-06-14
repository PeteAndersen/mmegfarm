from django.contrib.postgres.fields import ArrayField
from django.db import models


class Creature(models.Model):
    ARCHETYPE_DEFENDER = 'defender'
    ARCHETYPE_ATTACKER = 'attacker'
    ARCHETYPE_SABOTEUR = 'saboteur'
    ARCHETYPE_SUPPORT = 'support'

    ARCHETYPE_CHOICES = (
        (ARCHETYPE_ATTACKER, 'Attacker'),
        (ARCHETYPE_DEFENDER, 'Defender'),
        (ARCHETYPE_SABOTEUR, 'Saboteur'),
        (ARCHETYPE_SUPPORT, 'Support'),
    )

    ELEMENT_FIRE = 'fire'
    ELEMENT_WATER = 'water'
    ELEMENT_AIR = 'air'
    ELEMENT_EARTH = 'earth'
    ELEMENT_LIGHT = 'light'
    ELEMENT_DARK = 'dark'

    ELEMENT_CHOICES = (
        (ELEMENT_FIRE, 'Fire'),
        (ELEMENT_WATER, 'Water'),
        (ELEMENT_AIR, 'Air'),
        (ELEMENT_EARTH, 'Earth'),
        (ELEMENT_LIGHT, 'Light'),
        (ELEMENT_DARK, 'Dark'),
    )

    GROUP_BAD = 'bad'
    GROUP_AVG = 'avg'
    GROUP_GOOD = 'good'
    GROUP_VERYGOOD = 'veryGood'
    GROUP_OUTSTANDING = 'outstanding'

    GROUP_CHOICES = (
        (GROUP_BAD, 'Bad'),
        (GROUP_AVG, 'Average'),
        (GROUP_GOOD, 'Good'),
        (GROUP_VERYGOOD, 'Very Good'),
        (GROUP_OUTSTANDING, 'Outstanding'),
    )

    game_id = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=30)
    playable = models.BooleanField()
    summonable = models.BooleanField()
    inMenagerie = models.BooleanField()
    rank = models.IntegerField()
    archetype = models.CharField(choices=ARCHETYPE_CHOICES, max_length=15)
    element = models.CharField(choices=ELEMENT_CHOICES, max_length=10)
    group = models.CharField(choices=GROUP_CHOICES, max_length=15)
    subgroup = ArrayField(models.CharField(max_length=20), blank=True)
    lore = models.TextField(blank=True, default='')
    creatureType = models.CharField(max_length=50)
    trackingName = models.CharField(max_length=50)

    hp = models.IntegerField()
    attack = models.IntegerField()
    defense = models.IntegerField()
    criticalChance = models.IntegerField()
    criticalDamage = models.IntegerField()
    accuracy = models.FloatField()
    resistance = models.FloatField()
    initialSpeed = models.IntegerField()
    speed = models.FloatField()

    def __str__(self):
        return f'{self.name} - {self.get_element_display()} - {self.rank} star'

    class Meta:
        ordering = ['rank', 'name']