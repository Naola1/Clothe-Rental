from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .serializers import UserRegistrationSerializer, UserSerializer
from user.utils import generate_token

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self.send_activation_email_api(user, request)
        
        return Response({
            "message": "Registration successful. Please verify your email.",
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

    def send_activation_email_api(self, user, request):
        current_site = request.META.get('HTTP_HOST', 'localhost:8000')  
        email_subject = 'Activate your account'
        message = render_to_string('user/email_verification_api.html', {
            'user': user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user),
        })
    
        try:
            email = EmailMessage(email_subject, message, to=[user.email])
            email.content_subtype = 'html'
            email.send()
            return Response({'detail': 'Verification email sent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Failed to send verification email'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActivateAccountView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and generate_token.check_token(user, token):
            user.is_email_verified = True
            user.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Email verified successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        return Response({'error': 'Invalid activation link'}, status=status.HTTP_400_BAD_REQUEST)

