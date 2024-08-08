from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import re

class RegistrationForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Enter a valid email address.')

        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with that email already exists.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.is_password_strong(password):
            raise ValidationError('Password must be at least 8 characters long and include both letters and numbers.')
        return password

    def is_password_strong(self, password):
        if len(password) < 8:
            return False
        if not re.search(r'[A-Za-z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        return True

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
