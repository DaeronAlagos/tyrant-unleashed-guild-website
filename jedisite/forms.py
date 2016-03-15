from django import forms
from jedisite.models import GameAccount, Decks, UserProfile
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('is_officer', 'is_bot')


class GameAccountForm(forms.ModelForm):

    canvas = forms.URLField(label=u'Canvas Link', widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'http://'}))

    class Meta:
        model = GameAccount
        fields = ('canvas',)


class GameAccountBasicForm(forms.ModelForm):

    name = forms.CharField(max_length=128, label=u'Account Name', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Game Account Name'}))
    kong_name = forms.CharField(max_length=128, label=u'Kong Name', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kongregate Username'}))
    guild = forms.CharField(max_length=64, label=u'Guild', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guild Name'}))

    class Meta:
        model = GameAccount
        exclude = ('user', 'canvas', 'postdata', 'inventory')


class DeckForm(forms.ModelForm):

    MODE_CHOICES = (('Offense', 'Offense'),
                    ('Defense', 'Defense')
                    )

    mode = forms.ChoiceField(choices=MODE_CHOICES, required=True, label=u'Mode', widget=forms.Select(attrs={'class': 'form-control margin-bottom-10'}))

    TYPE_CHOICES = (('Brawl', 'Brawl'),
                    ('War', 'War'),
                    ('Conquest', 'Conquest')
                    )
    type = forms.ChoiceField(choices=TYPE_CHOICES, required=True, label=u'Type', widget=forms.Select(attrs={'class': 'form-control margin-bottom-10'}))

    class Meta:
        model = Decks
        exclude = ('guild', 'date',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DeckForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.ModelChoiceField(queryset=GameAccount.objects.filter(user=user), widget=forms.Select(attrs={'class': 'form-control margin-bottom-10'}))
        self.fields['deck'] = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'class': 'form-control margin-bottom-10', 'placeholder': 'Example: Commander, Card 1, Card 2, Card 3'}))
        self.fields['bge'] = forms.CharField(max_length=128, required=False, label=u'BGE', widget=forms.TextInput(attrs={'class': 'form-control margin-bottom-10', 'placeholder': 'Protect all 2, None, Triage (Must be 3 values)'}))
        self.fields['friendly_structures'] = forms.CharField(max_length=50, required=False, label=u'Friendly Structures', widget=forms.TextInput(attrs={'class': 'form-control margin-bottom-10', 'placeholder': 'Example: Death Factory, Death Factory'}))
        self.fields['enemy_structures'] = forms.CharField(max_length=50, required=False, label=u'Enemy Structures', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: Tesla Coil'}))
        #self.fields['guild'] = GameAccount.objects.all().filter(name=self.fields['name'])


class UpdatePostdataForm(forms.ModelForm):
    canvas = forms.URLField(widget=forms.HiddenInput())
    kong_name = forms.CharField(widget=forms.HiddenInput())

    #kong_name = forms.URLField(widget=forms.HiddenInput(attrs={'value': 'canvas'}))

    class Meta:
        model = GameAccount
        fields = ('canvas', )


class DeleteAccountForm(forms.ModelForm):
    kong_name = forms.URLField(widget=forms.HiddenInput())

    class Meta:
        model = GameAccount
        fields = ('name',)


class UserIsActiveForm(forms.ModelForm):
    is_active = forms.BooleanField()

    class Meta:
        model = User
        fields = ('is_active',)
