from rest_framework import viewsets, pagination

from bestiary.models import Creature
from .serializers import CreatureSerializer
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
    queryset = Creature.objects.filter(playable=True).prefetch_related(
        'evolvesTo',
        'spell_set',
        'spell_set__spelleffect_set',
        'spell_set__spellupgrade_set',
    )
    serializer_class = CreatureSerializer
    pagination_class = CreaturePagination
    filter_class = CreatureFilter
