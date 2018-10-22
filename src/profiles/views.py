
from rest_framework import viewsets, pagination

from .models import Account, CreatureInstance, GlyphInstance, Team
from .serializers import AccountSerializer, CreatureInstanceSerializer, GlyphInstanceSerializer, TeamSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class CreatureInstanceViewSet(viewsets.ModelViewSet):
    queryset = CreatureInstance.objects.all()
    serializer_class = CreatureInstanceSerializer


class GlyphInstanceViewSet(viewsets.ModelViewSet):
    queryset = GlyphInstance.objects.all()
    serializer_class = GlyphInstanceSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
