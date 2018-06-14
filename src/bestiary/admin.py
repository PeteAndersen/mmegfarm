from django.contrib import admin

from .models import *


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
