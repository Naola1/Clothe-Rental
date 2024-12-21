from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# Get the custom User model
User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput, 
        label="Password",
        error_messages={
            'required': 'Password is required.',
        }
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, 
        label="Confirm Password",
        error_messages={
            'required': 'Please confirm your password.',
        }
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'confirm_password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already in use.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data
