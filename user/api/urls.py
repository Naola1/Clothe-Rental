from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views  

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/', views.ActivateAccountView.as_view(), name='activate'),
    path("login/", views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('change-password/', views.ChangePasswordView.as_view(), 
         name='change_password'),
    path('password/reset/',views.PasswordResetRequestView.as_view(), 
         name='password_reset_request'),
    path('password/reset/confirm/',views.PasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('profile/', views.ProfileView.as_view(), name='profile_view'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
]