from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Username/Email', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    redir_url = forms.CharField(widget=forms.HiddenInput(), required=False)


class SignupForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    redir_url = forms.CharField(widget=forms.HiddenInput(), required=False)


class RfidCardPairForm(forms.Form):
    card_id = forms.IntegerField(
        label='Pair by card ID (defaults to last unpaired)',
        widget=forms.TextInput())


class PaymentForm(forms.Form):

    def __init__(self, *args, **kwargs):
        year_month_choices = kwargs.pop('year_month_choices')
        super().__init__(*args, **kwargs)
        self.fields['year_month'] = forms.ChoiceField(
            label='Inform the door of a payment',
            choices=[(i, i) for i in year_month_choices])

    def clean_year_month(self):
        yrm = self.cleaned_data['year_month'].split('-')
        return [int(i) for i in yrm]
