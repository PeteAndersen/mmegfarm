from django_filters import rest_framework as filters
from rest_framework import viewsets, pagination
from rest_framework.filters import OrderingFilter

from bestiary.models import Creature, Dungeon
from .serializers import CreatureSerializer, DungeonSerializer
from .filters import CreatureFilter


class CreaturePagination(pagination.PageNumberPagination):
    ordering = ['rank', 'name']
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 10000


class CreatureViewSet(viewsets.ModelViewSet):
    """
    Data for playable creatures in the game
    """
    queryset = Creature.objects.filter(playable=True).select_related(
        'evolvesTo'
    ).prefetch_related(
        'evolvesFrom',
        'spell_set',
        'spell_set__spelleffect_set',
        'spell_set__spellupgrade_set',
    )
    serializer_class = CreatureSerializer
    pagination_class = CreaturePagination
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter, )
    filter_class = CreatureFilter

class DungeonViewSet(viewsets.ModelViewSet):
    """
    Dungeon waves and drops
    """
    queryset = Dungeon.objects.all()
    serializer_class = DungeonSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter,)
