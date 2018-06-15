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

    spells = models.ManyToManyField('Spell', through='CreatureSpell')

    def __str__(self):
        return f'{self.name} - {self.get_element_display()} - {self.rank} star'

    class Meta:
        ordering = ['rank', 'name']


class Spell(models.Model):
    game_id = models.CharField(max_length=35)
    image = models.CharField(max_length=50)
    turns = models.IntegerField(blank=True, null=True)
    passive = models.BooleanField(default=False)
    passiveTrigger = models.CharField(max_length=30, blank=True, default='')

    def __str__(self):
        return self.game_id


class SpellEffect(models.Model):
    TARGET_ONE = 'one'
    TARGET_ALL = 'all'
    TARGET_SELF = 'self'
    TARGET_ONE_NOT_SELF = 'one_minus_self'
    TARGET_ALL_NOT_SELF = 'all_minus_self'
    TARGET_ALL_MINUS_ONE = 'all_minus_one'
    TARGET_RANDOM_DEAD = 'random_dead'

    TARGET_CHOICES = (
        (TARGET_ONE, 'One'),
        (TARGET_ALL, 'All'),
        (TARGET_SELF, 'Self'),
        (TARGET_ONE_NOT_SELF, 'One (excluding self)'),
        (TARGET_ALL_NOT_SELF, 'All (excluding self)'),
        (TARGET_ALL_MINUS_ONE, 'All (minus one)'),
        (TARGET_RANDOM_DEAD, 'Random Dead'),
    )

    CONDITION_CRIT = 'attackCriticalLaunched'
    CONDITION_HAS_DEBUFF = 'targetHasDebuff'
    CONDITION_SELF_HP_ABOVE = 'selfHpAbove'
    CONDITION_TARGET_HP_EQUAL = 'targetHpEquals'
    CONDITION_TARGET_HP_BELOW = 'targetHpBelow'
    CONDITION_TARGET_HP_ABOVE = 'targetHpAbove'
    CONDITION_LINK = 'link'

    CONDITION_CHOICES = (
        (CONDITION_CRIT, 'Critical Hit'),
        (CONDITION_HAS_DEBUFF, 'Target Has Debuff'),
        (CONDITION_SELF_HP_ABOVE, 'Own HP Above Threshold'),
        (CONDITION_TARGET_HP_EQUAL, 'Target HP Equals Threshold'),
        (CONDITION_TARGET_HP_ABOVE, 'Target HP Above Threshold'),
        (CONDITION_TARGET_HP_BELOW, 'Target HP Below Threshold'),
        (CONDITION_LINK, 'Link'),
    )

    spell = models.ForeignKey(Spell, on_delete=models.CASCADE)
    order = models.IntegerField()
    effect = models.CharField(max_length=30)
    target = models.CharField(choices=TARGET_CHOICES, max_length=20)
    condition = ArrayField(
        models.CharField(choices=CONDITION_CHOICES, max_length=30, default=''),
        blank=True
    )
    permanent = models.NullBooleanField()

    class Meta:
        ordering = ['order']


class SpellUpgrade(models.Model):
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE)
    order = models.IntegerField()
    game_id = models.CharField(max_length=50)
    amount = models.FloatField()
    is_percentage = models.BooleanField()
    attribute = models.CharField(max_length=10)
    description = models.CharField(max_length=150)

    class Meta:
        ordering = ['order']


class CreatureSpell(models.Model):
    # M2M through field for creature-unique attributes on spells
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE)
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE)
    order = models.IntegerField()
    title = models.CharField(max_length=80)
    description = models.TextField()
    image = models.CharField(max_length=50)
    params = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['order']
