from django.contrib.auth.models import User
from rest_framework import serializers

from bestiary.serializers import CreatureSerializer

from .models import Profile, Account, CreatureInstance, GlyphInstance, Team


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class GlyphInstanceSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    rarity = serializers.CharField(source='get_rarity_display')
    shape = serializers.CharField(source='get_shape_display')

    class Meta:
        model = GlyphInstance
        fields = (
            'id',
            'game_id',
            'owner',
            'creature',
            'type',
            'rarity',
            'shape',
            'stars',
            'level',
            'stats',
        )


class CreatureInstanceSerializer(serializers.ModelSerializer):
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


class AccountSerializer(serializers.ModelSerializer):
    creatures = serializers.PrimaryKeyRelatedField(source='creatureinstance_set', read_only=True, many=True)
    glyphs = serializers.PrimaryKeyRelatedField(source='glyphinstance_set', read_only=True, many=True)

    class Meta:
        model = Account
        fields = (
            'id',
            'owner',
            'name',
            'creatures',
            'glyphs'
        )


class ProfileSerializer(serializers.ModelSerializer):
    privacy = serializers.CharField(source='get_privacy_display')

    class Meta:
        model = Profile
        fields = (
            'privacy',
            'preferences',
            'friends',
        )


class UserDetailsSerializer(serializers.ModelSerializer):
    game_accounts = AccountSerializer(source='account_set', many=True, read_only=True)
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile', 'game_accounts']
