from rest_framework import serializers

from bestiary.models import Creature


class CreatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creature
        fields = '__all__'
