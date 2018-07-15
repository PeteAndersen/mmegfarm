from django_filters import rest_framework as filters
from rest_framework import viewsets, pagination
from rest_framework.filters import OrderingFilter

from bestiary.models import Creature, Dungeon, Level
from .serializers import CreatureSerializer, DungeonSerializer, LevelSerializer, LevelSummarySerializar
from .filters import CreatureFilter, DungeonFilter


class CreaturePagination(pagination.PageNumberPagination):
    ordering = ['rank', 'name']
    page_size = 50
    max_page_size = 10000
    page_size_query_param = 'page_size'


class CreatureViewSet(viewsets.ModelViewSet):
    """
    Data for playable creatures in the game
    """
    queryset = Creature.objects.filter(playable=True).select_related(
        'evolvesFrom'
    ).prefetch_related(
        'evolvesTo',
        'spell_set',
        'spell_set__spelleffect_set',
        'spell_set__spellupgrade_set',
    )
    serializer_class = CreatureSerializer
    pagination_class = CreaturePagination
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter, )
    filter_class = CreatureFilter


class DungeonPagination(pagination.PageNumberPagination):
    ordering = ['id']
    page_size = 25
    max_page_size = 10000
    page_size_query_param = 'page_size'


class DungeonViewSet(viewsets.ModelViewSet):
    """
    Dungeons with levels and rewards
    """
    queryset = Dungeon.objects.all().prefetch_related('level_set')
    serializer_class = DungeonSerializer
    pagination_class = DungeonPagination
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter, )
    filter_class = DungeonFilter


class LevelPagination(pagination.PageNumberPagination):
    ordering = ['order']
    page_size = 50
    max_page_size = 10000
    page_size_query_param = 'page_size'


class LevelViewSet(viewsets.ModelViewSet):
    """
    Levels with wave information when viewing a single instance
    """
    queryset = Level.objects.all()
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter,)

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action in ['retrieve']:
            queryset = queryset.prefetch_related(
                'wave_set',
                'wave_set__enemy_set',
                'wave_set__enemy_set__enemyspell_set',
                'wave_set__enemy_set__enemyspell_set__enemyspelleffect_set',
                'wave_set__boss_set',
                'wave_set__boss_set__bossspell_set',
                'wave_set__boss_set__bossspell_set__bossspelleffect_set',
            )

        return queryset

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            return LevelSummarySerializar
        else:
            return LevelSerializer