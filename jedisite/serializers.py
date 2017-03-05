from rest_framework import serializers
from jedisite.models import Decks, GameAccount


class DecksSerializer(serializers.ModelSerializer):

    # bge = serializers.CharField(required=False, allow_blank=True)
    # friendly_structures = serializers.CharField(required=False, allow_blank=True)
    # enemy_structures = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Decks
        exclude = ('id', )


class ForceAuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = GameAccount
        fields = ('postdata', )


# class AccountsSerializer(serializers.ModelSerializer):
class AccountsSerializer(serializers.Serializer):

    postdata = serializers.CharField(max_length=2048)
    kong_name = serializers.CharField(max_length=64)
    name = serializers.CharField(max_length=64)
    guild = serializers.CharField(max_length=64)
    inventory = serializers.ListField()
    deck = serializers.JSONField()

    # class Meta:

        # model = GameAccount
        # fields = ("postdata", "kong_name", "name", "guild", "inventory", "deck")


class InventorySerializer(serializers.ListSerializer):

    child = serializers.JSONField()
