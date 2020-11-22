from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Round, Player, Clue


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    username = serializers.CharField()
    first_name = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name')

    def create(self, data):
        user = User.objects.create_user(username=data['username'],
                                        email=data['email'],first_name=data['first_name'])
        return user


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('name', 'first_name', 'email', 'imageLink', 'score', 'roundNo')


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ('question', 'round_number','audio','image')
