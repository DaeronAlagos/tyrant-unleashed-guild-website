from django import forms
from jedisite.models import GameAccount, Decks, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
import utils.tyrant_utils as tyrant_utils
import re


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('line_name',)


class SetPasswordForm(forms.Form):

    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
    }
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'class': 'form-control margin-bottom-10'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control margin-bottom-10'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': "Your old password was entered incorrectly.",
    })
    old_password = forms.CharField(
        label="Old password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': '', 'class': 'form-control margin-bottom-10'}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password


class GameAccountForm(forms.ModelForm):
    postdata = forms.CharField(label=u'Postdata',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''})
                               )

    def clean_postdata(self):
        postdata = self.cleaned_data['postdata']
        tyrant_api = tyrant_utils.TyrantAPI()
        postdata_params = tyrant_api.get_postdata_params(postdata)
        if GameAccount.objects.filter(kong_name=str(postdata_params['kong_name'][0])).exists():
            raise forms.ValidationError("Account already exists!")

        return postdata

    class Meta:
        model = GameAccount
        fields = ('postdata',)


class GameAccountBasicForm(forms.ModelForm):
    GUILD_CHOICES = (
        ('MasterJedis', 'MasterJedis'),
        ('Quasar', 'Quasar'),
        ('Corona', 'Corona'),
    )

    name = forms.CharField(
        max_length=128,
        label=u'Account Name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Game Account Name'
            }
        )
    )

    kong_name = forms.CharField(
        max_length=128,
        label=u'Kong Name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 'placeholder': 'Kongregate Username'
            }
        )
    )

    guild = forms.ChoiceField(
        choices=GUILD_CHOICES,
        required=True,
        label=u'Guild',
        widget=forms.Select(
            attrs={
                'class': 'form-control margin-bottom-10'
            }
        )
    )

    class Meta:
        model = GameAccount
        exclude = ('user', 'canvas', 'postdata', 'inventory', 'show_canvas', 'allow_command')


class ChangeGuildForm(forms.ModelForm):
    GUILD_CHOICES = (
        ('MasterJedis', 'MasterJedis'),
        ('Quasar', 'Quasar'),
        ('CorNox', 'CorNox'),
    )

    guild = forms.ChoiceField(
        choices=GUILD_CHOICES,
        required=False,
        label=u'Guild',
        widget=forms.Select(
            attrs={
                'class': 'form-control change_guild'
            }
        ),
    )

    class Meta:
        model = GameAccount
        fields = ('guild',)


class DeckForm(forms.ModelForm):
    MODE_CHOICES = (('Offense', 'Offense'),
                    ('Defense', 'Defense')
                    )

    mode = forms.ChoiceField(
        choices=MODE_CHOICES,
        required=True,
        label=u'Mode',
        widget=forms.Select(
            attrs={
                'class': 'form-control margin-bottom-10'
            }
        )
    )

    TYPE_CHOICES = (
        ('Faction', 'War'),
        ('Brawl', 'Brawl'),
        ('Conquest', 'Conquest')
    )

    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=True,
        label=u'Type',
        widget=forms.Select(
            attrs={
                'class': 'form-control margin-bottom-10'
            }
        )
    )

    structures = [
        'Tesla Coil-4',
        'Minefield-4',
        'Foreboding Archway-4',
        'Forcefield-4',
        'Illuminary Blockade-4',
        'Inspiring Altar-4',
        'Death Factory-4',
        'Lightning Cannon-4',
        'Sky Fortress-4',
        'Mortar Tower-4',
        'Corrosive Spore-4'
    ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DeckForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.ModelChoiceField(queryset=GameAccount.objects.filter(user=user).order_by('name'),
                                                     widget=forms.Select(
                                                         attrs={'class': 'form-control margin-bottom-10'}))
        self.fields['deck'] = forms.CharField(max_length=256, widget=forms.TextInput(
            attrs={'class': 'form-control margin-bottom-10',
                   'placeholder': 'Example: Commander, Card 1, Card 2, Card 3'}))
        self.fields['bge'] = forms.CharField(max_length=128, required=False, label=u'BGE', widget=forms.TextInput(
            attrs={'class': 'form-control margin-bottom-10',
                   'placeholder': 'Example: Protect all 2, None, Triage (Leave blank for Benchmark)'}))
        self.fields['friendly_structures'] = forms.CharField(max_length=50, required=False,
                                                             label=u'Friendly Structures', widget=forms.TextInput(
                attrs={'class': 'form-control margin-bottom-10',
                       'placeholder': 'Example: Death Factory, Death Factory'}))
        self.fields['enemy_structures'] = forms.CharField(max_length=50, required=False, label=u'Enemy Structures',
                                                          widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                        'placeholder': 'Example: Tesla Coil'}))
        # self.fields['guild'] = GameAccount.objects.all().filter(name=self.fields['name'])

    def clean_deck(self):

        deck = self.cleaned_data['deck']
        card_reader = tyrant_utils.CardReader()
        player_cards_list = deck.split(',')
        cards = card_reader.cards_list
        for card in player_cards_list:
            m = re.search(r"^\s?(.*?[\d]?)(-\d)?[ ]?#?(\d{1,2})?$", card)
            print "Clean Deck:", (unicode(m.group(1)))
            if not any(d['card_name'] == unicode(m.group(1)) for d in cards):
                raise forms.ValidationError(card + " is not a valid card!")

        return deck

    def clean_friendly_structures(self):

        friendly_structures = self.cleaned_data['friendly_structures']
        if friendly_structures == "":
            return friendly_structures
        else:
            friendly_structures_list = friendly_structures.split(",")
            for idx, structure in enumerate(friendly_structures_list):
                friendly_structures_list[idx] = structure.strip().title() + "-4"
                if friendly_structures_list[idx] not in self.structures:
                    raise forms.ValidationError(structure + " is not a valid Structure!")

            return ", ".join(friendly_structures_list)

    def clean_enemy_structures(self):

        enemy_structures = self.cleaned_data['enemy_structures']
        if enemy_structures == "":
            return enemy_structures
        else:
            enemy_structures_list = enemy_structures.split(",")
            for idx, structure in enumerate(enemy_structures_list):
                enemy_structures_list[idx] = structure.strip().title() + "-4"
                if enemy_structures_list[idx] not in self.structures:
                    raise forms.ValidationError(structure + " is not a valid Structure")

            return ", ".join(enemy_structures_list)

    class Meta:
        model = Decks
        exclude = ('guild', 'date',)


class UpdatePostdataForm(forms.ModelForm):
    canvas = forms.URLField(
        widget=forms.HiddenInput()
    )
    kong_name = forms.CharField(
        widget=forms.HiddenInput()
    )

    # kong_name = forms.URLField(widget=forms.HiddenInput(attrs={'value': 'canvas'}))

    class Meta:
        model = GameAccount
        fields = ('canvas',)


class DeleteAccountForm(forms.ModelForm):
    kong_name = forms.URLField(
        widget=forms.HiddenInput()
    )

    class Meta:
        model = GameAccount
        fields = ('name',)


class UserIsActiveForm(forms.ModelForm):
    is_active = forms.BooleanField()

    class Meta:
        model = User
        fields = ('is_active',)


class AllowCommandForm(forms.ModelForm):
    allow_command = forms.BooleanField(
        required=False
    )

    class Meta:
        model = GameAccount
        fields = ('allow_command',)


class UploadInventoryForm(forms.ModelForm):
    inventory = forms.CharField(
        label=u'Owned Cards',
        widget=(
            forms.Textarea(
                attrs={
                    'class': 'form-control word-count',
                    'data-info': 'textarea-words-info',
                    'placeholder': 'Enter cards here, one card per line',
                    'rows': '5'
                }
            )
        ),
    )

    def clean_inventory(self):

        player_card_list = self.cleaned_data['inventory'].splitlines()
        card_reader = tyrant_utils.CardReader()
        cards = card_reader.cards_list
        global_card_list = []
        for card in player_card_list:
            m = re.search("^\s?(.*?[\d]?)(-\d)?[ ]?#?(\d{1,2})?$", card)
            # print(str(m.group(1)))
            if not [d['card_name'] == str(m.group(1)) for d in cards]:
                raise forms.ValidationError(card + " is not a valid card!")

        return player_card_list

    class Meta:
        model = GameAccount
        fields = ('inventory',)
