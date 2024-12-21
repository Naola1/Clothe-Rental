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


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Authenticate user
            user = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user:
                # Check if email is verified
                if not user.is_email_verified:
                    form.add_error(None, 'Email not verified. Please check your email for the verification link.')
                    return render(request, 'user/login.html', {'form': form})
                
                # Log in the user
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'user/login.html', {'form': form})



@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

def forgot_password_view(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                send_password_reset_email(request, user)
                messages.success(request, "A password reset link has been sent to your email.")
                return redirect("login")
            messages.error(request, "No user associated with this email.")
    else:
        form = PasswordResetForm()
    return render(request, "user/forgot_password.html", {"form": form})


def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password reset successfully.")
                return redirect("login")
        else:
            form = SetPasswordForm(user)
        return render(request, "user/reset_password.html", {"form": form, "uidb64": uidb64, "token": token})

    messages.error(request, "Invalid or expired reset password link.")
    return redirect("forgot_password")


def send_password_reset_email(request, user):
    subject = "Password Reset Requested"
    email_template_name = "user/password_reset_email.html"
    context = {
        "email": user.email,
        "domain": request.META['HTTP_HOST'],
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user),
        "protocol": "http" if settings.DEBUG else "https",
    }
    
    email_content = render_to_string(email_template_name, context)
    
    # Create the email using EmailMessage
    email = EmailMessage(subject, email_content, settings.EMAIL_HOST_USER, [user.email])
    email.content_subtype = 'html'  # Set the content type to HTML
    
    try:
        email.send()  # Send the email
    except Exception as e:
        print(f"Failed to send email: {e}")


@login_required
def profile_view(request):
    return render(request, 'user/profile.html', {'user': request.user})


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    return render(request, 'user/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully.')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user/change_password.html', {'form': form})
