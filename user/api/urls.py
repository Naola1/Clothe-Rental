from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views  

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='api_register'),
    path('activate/<str:uidb64>/<str:token>/', views.ActivateAccountView.as_view(), name='api_activate'),
    path("login/", views.LoginView.as_view(), name="api_login"),
    path('logout/', views.LogoutView.as_view(), name='api_logout'),
    path('change-password/', views.ChangePasswordView.as_view(), 
         name='api_change-password'),
    path('password/reset/',views.PasswordResetRequestView.as_view(), 
         name='api_password_reset_request'),
    path('password/reset/confirm/',views.PasswordResetConfirmView.as_view(), 
         name='api_passwrd_reset_confirm'),
    path('profile/', views.ProfileView.as_view(), name='api_profile_view'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='api_profile_update'),
]