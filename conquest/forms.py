from django import forms
from jedisite.models import GameAccount, Decks
from django.contrib.auth.models import User


class ConquestCommand(forms.Form):
    choices = forms.MultipleChoiceField(

    )
    attacks = forms.IntegerField()
