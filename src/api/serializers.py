from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer


class UserDetailsSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']