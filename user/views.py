from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.conf import settings
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings

from .forms import LoginForm, UserRegistrationForm, UserProfileUpdateForm
from .models import User

# Get the custom User model
User = get_user_model()

def send_activation_email(user, request):
    current_site = request.META['HTTP_HOST']
    subject = 'Email Verification'
    message = render_to_string('user/email_verification.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user),
    })
    email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [user.email])
    email.content_subtype = 'html'
    try:
        email.send()
    except Exception as e:
        print(f"Failed to send email: {e}")



def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            send_activation_email(user, request)
            messages.success(request, 'We sent you an email to verify your account')
            return redirect('login')
        # If form is not valid, the errors will be passed to the template
    else:
        form = UserRegistrationForm()

    return render(request, 'user/register.html', {'form': form})

def activate_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        messages.success(request, 'Email verified. You can now login.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('login')
