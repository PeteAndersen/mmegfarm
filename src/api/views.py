from rest_framework import viewsets, pagination

from bestiary.models import Creature

from .serializers import *


class CreaturePagination(pagination.CursorPagination):
    ordering = ['rank', 'name']
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 10000


class CreatureViewSet(viewsets.ModelViewSet):
    queryset = Creature.objects.filter(playable=True).prefetch_related(
        'spell_set',
        'spell_set__spelleffect_set',
        'spell_set__spellupgrade_set',
    )
    serializer_class = CreatureSerializer
    pagination_class = CreaturePagination
