from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Username/Email', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class SignupForm(forms.Form):
    username = forms.CharField(label='Username (optional)', max_length=50,
                               required=False)
    email = forms.EmailField(label='Email', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class RfidCardPairForm(forms.Form):
    card_id = forms.IntegerField(label='Pair by card ID')


class PaymentForm(forms.Form):

    def __init__(self, *args, **kwargs):
        year_month_choices = kwargs.pop('year_month_choices')
        super().__init__(*args, **kwargs)
        self.fields['year_month'] = forms.ChoiceField(
            label='Submit payment',
            choices=[(i, i) for i in year_month_choices])

    def clean_year_month(self):
        yrm = self.cleaned_data['year_month'].split('-')
        return [int(i) for i in yrm]
