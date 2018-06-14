from rest_framework import viewsets, pagination

from bestiary.models import Creature

from .serializers import *


class CreaturePagination(pagination.CursorPagination):
    ordering = ['rank', 'name']
    page_size = 100


class CreatureViewSet(viewsets.ModelViewSet):
    queryset = Creature.objects.filter(playable=True)
    serializer_class = CreatureSerializer
    pagination_class = CreaturePagination
