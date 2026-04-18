from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CipherRegistrationForm(UserCreationForm):
    # Add the email field explicitly
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        # Include email in the fields list
        fields = ("username", "email")