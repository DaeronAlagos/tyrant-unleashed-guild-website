from rest_framework import serializers
from jedisite.models import Decks, GameAccount


class DecksSerializer(serializers.ModelSerializer):

    bge = serializers.CharField(required=False, allow_blank=True)
    friendly_structures = serializers.CharField(required=False, allow_blank=True)
    enemy_structures = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Decks
        exclude = ('id', )


class ForceAuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = GameAccount
        fields = ('postdata', )
