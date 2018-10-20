from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from bestiary.serializers import CreatureSerializer

from .models import Profile, CreatureInstance, GlyphInstance, Team


class UserDetailsSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProfileSerializer(ModelSerializer):
    owner = UserDetailsSerializer()

    class Meta:
        model = Profile
        fields = '__all__'


class CreatureInstanceSerializer(ModelSerializer):
    creature = CreatureSerializer(read_only=True)

    class Meta:
        model = CreatureInstance
        fields = [
            'id',
            'game_id',
            'owner',
            'creature',
            'rank',
            'level',
        ]


class GlyphInstanceSerializer(ModelSerializer):
    class Meta:
        model = GlyphInstance
        fields = '__all__'


class TeamSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
