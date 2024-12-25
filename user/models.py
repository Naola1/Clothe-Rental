from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator

# Custom user manager to handle user creation (including superusers)
class CustomUserManager(BaseUserManager):
      # Method to create a standard use
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    # Method to create a superuser with elevated privileges
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

# Custom User model
class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    # Defining user fields
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, 
                                    validators=[RegexValidator(regex=r'^\d{10,15}$', message="Phone number must be between 10 and 15 digits.")])
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True1)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=50, blank=True, null=True)
    rented_items = models.ForeignKey('shop.Rental', on_delete=models.CASCADE, null=True, blank=True, related_name='rented_by_user'  )
    # User status fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_email_verified = models.BooleanField(default=False)
    # Field used to log in
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()
    # String representation
    def __str__(self):
        return self.username
    # Method to get full name
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"