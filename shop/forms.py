from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.bootstrap import StrictButton


class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    email = forms.CharField(label='Email', max_length=1024)
    password = forms.PasswordInput()
    passwordconfirm = forms.PasswordInput()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-8'
        self.helper.layout = Layout(
            'username'
            'email',
            'password',
            'passwordconfirm',
            StrictButton('Log in', css_class='btn-default'))
