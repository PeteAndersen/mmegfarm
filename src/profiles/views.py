
from rest_framework import viewsets, pagination

from .models import Profile, CreatureInstance, GlyphInstance, Team
from .serializers import ProfileSerializer, CreatureInstanceSerializer, GlyphInstanceSerializer, TeamSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class CreatureInstanceViewSet(viewsets.ModelViewSet):
    queryset = CreatureInstance.objects.all()
    serializer_class = CreatureInstanceSerializer


class GlyphInstanceViewSet(viewsets.ModelViewSet):
    queryset = GlyphInstance.objects.all()
    serializer_class = GlyphInstanceSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
