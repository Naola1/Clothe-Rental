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

class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=255, 
        label="Email",
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.'
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput, 
        label="Password",
        error_messages={
            'required': 'Password is required.',
        }
    )

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 
            'last_name', 
            'username', 
            'gender', 
            'phone_number', 
            'address', 
            'profile_picture'
        ]

    def clean_username(self):
        username = self.cleaned_data['username']
        # Check if username is unique, excluding current user
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError("This username is already in use.")
        return username