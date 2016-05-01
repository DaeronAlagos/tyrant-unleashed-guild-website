from django import forms
from jedisite.models import GameAccount, Decks, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import password_validation


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
    """
    A form that lets a user change set their password without entering the old
    password
    """
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

    canvas = forms.URLField(label=u'Canvas Link',
                            widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'http://'})
                            )

    class Meta:
        model = GameAccount
        fields = ('canvas',)


class GameAccountBasicForm(forms.ModelForm):

    name = forms.CharField(max_length=128,
                           label=u'Account Name',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Game Account Name'})
                           )
    kong_name = forms.CharField(max_length=128,
                                label=u'Kong Name',
                                widget=forms.TextInput(attrs={
                                    'class': 'form-control', 'placeholder': 'Kongregate Username'}
                                ))
    guild = forms.CharField(max_length=64,
                            label=u'Guild',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guild Name'})
                            )

    class Meta:
        model = GameAccount
        exclude = ('user', 'canvas', 'postdata', 'inventory', 'show_canvas', 'allow_command')


class DeckForm(forms.ModelForm):

    MODE_CHOICES = (('Offense', 'Offense'),
                    ('Defense', 'Defense')
                    )

    mode = forms.ChoiceField(choices=MODE_CHOICES, required=True, label=u'Mode', widget=forms.Select(attrs={'class': 'form-control margin-bottom-10'}))

    TYPE_CHOICES = (('Brawl', 'Brawl'),
                    ('Faction', 'War'),
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


class ShowCanvasForm(forms.ModelForm):

    class Meta:
        model = GameAccount
        fields = ('show_canvas',)


class AllowCommandForm(forms.ModelForm):

    allow_command = forms.BooleanField(required=False)

    class Meta:
        model = GameAccount
        fields = ('allow_command',)
