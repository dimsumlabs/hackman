from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Username/Email', max_length=255)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class RfidCardPairForm(forms.Form):
    card_id = forms.IntegerField(label='Pair by card ID')
