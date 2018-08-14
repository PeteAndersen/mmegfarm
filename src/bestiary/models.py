from math import log, exp

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.utils.text import slugify


class CreatureBase(models.Model):
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

    game_id = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=30)
    playable = models.BooleanField(default=False)
    trackingName = models.CharField(max_length=50, blank=True, null=True)

    rank = models.IntegerField()
    archetype = models.CharField(choices=ARCHETYPE_CHOICES, max_length=15)
    element = models.CharField(choices=ELEMENT_CHOICES, max_length=10)

    hp = models.IntegerField()
    attack = models.IntegerField()
    defense = models.IntegerField()
    speed = models.FloatField()
    initialSpeed = models.IntegerField()
    criticalChance = models.IntegerField()
    criticalDamage = models.IntegerField()
    accuracy = models.FloatField()
    resistance = models.FloatField()

    class Meta:
        abstract = True

    RANK_UP_MULTIPLIERS = {
        'hp': {1: 1.651, 2: 2.064, 3: 1.803, 4: 1.537, 5: 1.461},
        'attack': {1: 1.689, 2: 2.540, 3: 1.905, 4: 1.537, 5: 1.461},
        'defense': {1: 1.689, 2: 2.540, 3: 1.905, 4: 1.537, 5: 1.461},
    }


class Creature(CreatureBase):
    GROUP_UNDEFINED = 'undefined'
    GROUP_BAD = 'bad'
    GROUP_AVG = 'avg'
    GROUP_GOOD = 'good'
    GROUP_VERYGOOD = 'veryGood'
    GROUP_OUTSTANDING = 'outstanding'

    GROUP_CHOICES = (
        (GROUP_UNDEFINED, 'Undefined'),
        (GROUP_BAD, 'Bad'),
        (GROUP_AVG, 'Average'),
        (GROUP_GOOD, 'Good'),
        (GROUP_VERYGOOD, 'Very Good'),
        (GROUP_OUTSTANDING, 'Outstanding'),
    )

    group = models.CharField(choices=GROUP_CHOICES, max_length=15)
    subgroup = ArrayField(models.CharField(max_length=20), blank=True)
    inMenagerie = models.BooleanField()
    summonable = models.BooleanField(default=False)
    evolvesFrom = models.ForeignKey(
        'Creature',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='evolvesTo',
    )
    lore = models.TextField(blank=True, default='')
    creatureType = models.CharField(max_length=50)

    evoHp = models.IntegerField(default=0)
    evoAttack = models.IntegerField(default=0)
    evoDefense = models.IntegerField(default=0)
    evoCriticalChance = models.IntegerField(default=0)
    maxLvlHp = models.IntegerField(blank=True, null=True)
    maxLvlAttack = models.IntegerField(blank=True, null=True)
    maxLvlDefense = models.IntegerField(blank=True, null=True)

    slug = models.SlugField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['rank', 'name']

    def save(self, *args, **kwargs):
        self.maxLvlHp = self.get_hp(5, self.max_level_for_rank(5))
        self.maxLvlAttack = self.get_attack(5, self.max_level_for_rank(5))
        self.maxLvlDefense = self.get_defense(5, self.max_level_for_rank(5))

        if self.pk:
            self.slug = slugify(f'{self.pk}-{self.name}-{self.element}')

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.get_element_display()} - {self.rank}*'

    @staticmethod
    def max_level_for_rank(rank):
        return 10 + rank * 5

    def get_hp(self, rank, level):
        return self._get_stat(
            self.rank,
            self.hp,
            self.evoHp,
            self.RANK_UP_MULTIPLIERS['hp'],
            rank,
            level
        )

    def get_attack(self, rank, level):
        return self._get_stat(
            self.rank,
            self.attack,
            self.evoAttack,
            self.RANK_UP_MULTIPLIERS['attack'],
            rank,
            level
        )

    def get_defense(self, rank, level):
        return self._get_stat(
            self.rank,
            self.defense,
            self.evoDefense,
            self.RANK_UP_MULTIPLIERS['defense'],
            rank,
            level
        )

    @staticmethod
    def _get_stat(base_rank, base_stat, evo_stat, multipliers, rank, level):
        max_lvl = Creature.max_level_for_rank(rank)

        # Get min/max stat for requested rank
        max_stat = (base_stat - evo_stat) * multipliers[base_rank]

        for r in range(base_rank, rank):
            max_stat = max_stat / 1.27 * multipliers[r + 1]

        max_stat = round(max_stat)

        if level == max_lvl:
            return max_stat + evo_stat
        else:
            # Calculate exponential curve for stats between level 1 and max
            a = base_stat
            b = log(max_stat / base_stat) / (max_lvl-1)
            x = level - 1

            return int(round(a*exp(b*x))) + evo_stat


class SpellBase(models.Model):
    slot = models.IntegerField(default=1)
    game_id = models.CharField(max_length=35)
    title = models.CharField(max_length=80)
    description = models.TextField()
    image = models.CharField(max_length=50)
    type_image = models.CharField(max_length=50, default='')
    turns = models.IntegerField(blank=True, null=True)
    passive = models.BooleanField(default=False)
    passiveTrigger = models.CharField(max_length=30, blank=True, default='')

    class Meta:
        abstract = True


class Spell(SpellBase):
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE)
    order = models.IntegerField()

    def __str__(self):
        return self.game_id

    class Meta:
        ordering = ['order']
        unique_together = ('creature', 'order')


class SpellEffectBase(models.Model):
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

    order = models.IntegerField()
    effect = models.CharField(max_length=30)
    target = models.CharField(choices=TARGET_CHOICES, max_length=20)
    params = JSONField(blank=True, default=dict)
    condition = ArrayField(
        models.CharField(choices=CONDITION_CHOICES, max_length=30, default=''),
        blank=True, default=list
    )
    permanent = models.NullBooleanField()
    probability = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True


class SpellEffect(SpellEffectBase):
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE)

    class Meta:
        ordering = ['order']
        unique_together = ('spell', 'order')


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
        unique_together = ('spell', 'order')


class Dungeon(models.Model):
    GROUP_ELEMENT = 'GroupElements'
    GROUP_GLYPH = 'GroupGlyphs'
    GROUP_TWIN_TOWERS = 'GroupTwinTowers'
    GROUP_EVENT = 'GroupEventDungeon'
    GROUP_SCENARIO = 'ScenarioDungeon'

    GROUP_CHOICES = (
        (GROUP_ELEMENT, 'Elemental Dungeon'),
        (GROUP_GLYPH, 'Glyph Dungeon'),
        (GROUP_TWIN_TOWERS, 'Tower of Trials'),
        (GROUP_EVENT, 'Event Dungeon'),
        (GROUP_SCENARIO, 'Shattered Islands Scenario'),
    )

    game_id = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=100)
    group = models.CharField(max_length=25, choices=GROUP_CHOICES)
    always_available = models.BooleanField(default=True)
    days_available = ArrayField(
        models.IntegerField(),
        default=list
    )
    months_available = ArrayField(
        models.IntegerField(),
        default=list
    )

    class Meta:
        ordering = ['pk']


class Level(models.Model):
    DIFFICULTY_EASY = 1
    DIFFICULTY_MEDIUM = 2
    DIFFICULTY_HARD = 3

    DIFFICULTY_CHOICES = (
        (DIFFICULTY_EASY, 'Normal'),
        (DIFFICULTY_MEDIUM, 'Advanced'),
        (DIFFICULTY_HARD, 'Nightmare'),
    )

    dungeon = models.ForeignKey(Dungeon, on_delete=models.CASCADE)
    game_id = models.CharField(max_length=50, db_index=True)
    order = models.IntegerField()
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, null=True, blank=True)
    slots = models.IntegerField(help_text='Number of creatures allowed to bring')
    energy_cost = models.IntegerField()
    rewards = JSONField(default=dict)
    rewards_instant = JSONField(default=dict, help_text='Rewards when using an Instant Ticket')

    class Meta:
        ordering = ['difficulty', 'order']


class Wave(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    game_id = models.CharField(max_length=50, db_index=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']


class Enemy(CreatureBase):
    BOSS_TYPE_MINIBOSS = 'miniBoss'
    BOSS_TYPE_BOSS = 'boss'
    BOSS_TYPE_CHOICES = (
        (BOSS_TYPE_MINIBOSS, 'Miniboss'),
        (BOSS_TYPE_BOSS, 'Boss'),
    )

    wave = models.ForeignKey(Wave, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    boss_type = models.CharField(
        max_length=10,
        choices=BOSS_TYPE_CHOICES,
        blank=True,
        null=True
    )
    level = models.IntegerField()

    class Meta:
        ordering = ['order']

    @staticmethod
    def max_level_for_rank(rank):
        return 10 + rank * 5

    @staticmethod
    def get_hp(base_rank, base_stat, rank, level):
        return Enemy._get_stat(
            base_rank,
            base_stat,
            Enemy.RANK_UP_MULTIPLIERS['hp'],
            rank,
            level
        )

    @staticmethod
    def get_attack(base_rank, base_stat, rank, level):
        return Enemy._get_stat(
            base_rank,
            base_stat,
            Enemy.RANK_UP_MULTIPLIERS['attack'],
            rank,
            level
        )

    @staticmethod
    def get_defense(base_rank, base_stat, rank, level):
        return Enemy._get_stat(
            base_rank,
            base_stat,
            Enemy.RANK_UP_MULTIPLIERS['defense'],
            rank,
            level
        )

    @staticmethod
    def _get_stat(base_rank, base_stat, multipliers, rank, level):
        max_lvl = Creature.max_level_for_rank(rank)

        # Get min/max stat for requested rank
        max_stat = base_stat * multipliers[base_rank]

        for r in range(base_rank, rank):
            max_stat = max_stat / 1.27 * multipliers[r + 1]

        max_stat = round(max_stat)

        if level == max_lvl:
            return max_stat
        else:
            # Calculate exponential curve for stats between level 1 and max
            a = base_stat
            b = log(max_stat / base_stat) / (max_lvl - 1)
            x = level - 1

            return int(round(a * exp(b * x)))


class EnemySpell(SpellBase):
    creature = models.ForeignKey(Enemy, on_delete=models.CASCADE)

    class Meta:
        ordering = ['slot']
        unique_together = ('creature', 'slot')


class EnemySpellEffect(SpellEffectBase):
    spell = models.ForeignKey(EnemySpell, on_delete=models.CASCADE)

    class Meta:
        ordering = ['order']
        unique_together = ('spell', 'order')
