from django.contrib import admin

from .models import *


class CreatureSpellInline(admin.TabularInline):
    model = CreatureSpell
    extra = 0


@admin.register(Creature)
class CreatureAdmin(admin.ModelAdmin):
    list_filter = (
        'playable',
        'summonable',
        'inMenagerie',
        'rank',
        'archetype',
        'element',
        'group',
    )

    inlines = [
        CreatureSpellInline,
    ]


class SpellEffectInline(admin.TabularInline):
    model = SpellEffect
    extra = 0


class SpellUpgradeInline(admin.TabularInline):
    model = SpellUpgrade
    ordering = ['order']
    extra = 0


@admin.register(Spell)
class SpellAdmin(admin.ModelAdmin):
    inlines = [
        SpellEffectInline,
        SpellUpgradeInline,
    ]
