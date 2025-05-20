from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login, logout, get_user_model

from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken

from allauth.account import app_settings as allauth_settings
from allauth.account.models import EmailAddress

from .auth_serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    UserDetailsSerializer, 
    PasswordChangeSerializer
)

User = get_user_model()


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserDetailsSerializer(user, context=self.get_serializer_context()).data
        }
        
        return Response(data, status=status.HTTP_201_CREATED)
        
    def perform_create(self, serializer):
        return serializer.save()


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserDetailsSerializer(user, context=self.get_serializer_context()).data
        }
        
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"detail": _("Successfully logged out.")}, status=status.HTTP_200_OK)


class UserDetailsView(RetrieveUpdateAPIView):
    serializer_class = UserDetailsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordChangeView(GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("New password has been saved.")}, status=status.HTTP_200_OK)
