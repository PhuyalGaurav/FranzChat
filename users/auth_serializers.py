from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from allauth.account.adapter import get_adapter
from allauth.account import app_settings as allauth_settings
from allauth.utils import get_username_max_length
from allauth.account.models import EmailAddress

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        max_length=get_username_max_length(),
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password1']
        )

        # Create EmailAddress instance for email verification if needed
        EmailAddress.objects.create(
            user=user,
            email=validated_data['email'],
            primary=True,
            verified=allauth_settings.EMAIL_VERIFICATION == 'none'
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            raise serializers.ValidationError(
                _("Must include 'email' and 'password'.")
            )
        return user

    def _validate_username(self, username, password):
        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            raise serializers.ValidationError(
                _("Must include 'username' and 'password'.")
            )
        return user

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        if email:
            user = self._validate_email(email, password)
        elif username:
            user = self._validate_username(username, password)
        else:
            raise serializers.ValidationError(
                _("Must include either 'username' or 'email'.")
            )

        if user:
            if not user.is_active:
                raise serializers.ValidationError(_('User account is disabled.'))
        else:
            raise serializers.ValidationError(
                _('Unable to log in with provided credentials.')
            )

        attrs['user'] = user
        return attrs


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'bio')
        read_only_fields = ('email',)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password2": "The two password fields didn't match."})
        validate_password(attrs['new_password1'], self.context['request'].user)
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user
