from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from .models import Profile, CreatureInstance, GlyphInstance

class UserDetailsSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CreatureInstanceSerializer(ModelSerializer):
    class Meta:
        model =