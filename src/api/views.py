from rest_framework import viewsets, pagination

from bestiary.models import Creature

from .serializers import *


class CreaturePagination(pagination.CursorPagination):
    ordering = ['rank', 'name']
    page_size = 100


class CreatureViewSet(viewsets.ModelViewSet):
    queryset = Creature.objects.filter(playable=True).prefetch_related(
        'creaturespell_set',
        'creaturespell_set__spell',
        'creaturespell_set__spell__spelleffect_set',
        'creaturespell_set__spell__spellupgrade_set',
    )
    serializer_class = CreatureSerializer
    pagination_class = CreaturePagination
