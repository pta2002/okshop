from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email, validate_slug, MinLengthValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150,
                               validators=[validate_slug], required=True)
    email = forms.CharField(label='Email', max_length=1024,
                            validators=[validate_email], required=True)
    password = forms.CharField(widget=forms.PasswordInput,
                               validators=[MinLengthValidator(8)],
                               label='Password', required=True)
    passwordconfirm = forms.CharField(widget=forms.PasswordInput,
                                      label='Confirm password', required=True)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('passwordconfirm'):
            raise forms.ValidationError("Passwords don't match!")
        if User.objects.filter(username=cleaned_data.get('username')).count() > 0:
            raise forms.ValidationError("Username already in use!")
        if User.objects.filter(email=cleaned_data.get('email')).count() > 0:
            raise forms.ValidationError("Email already in use!")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Register'))

