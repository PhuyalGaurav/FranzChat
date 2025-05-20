from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FriendRequest

User = get_user_model()


class FriendRequestSerializer(serializers.ModelSerializer):
    # Automatically set the sender to the current user
    from_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    to_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    friends = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    sent_requests = FriendRequestSerializer(
        source='sent_friend_requests',
        many=True,
        read_only=True
    )
    received_requests = FriendRequestSerializer(
        source='received_friend_requests',
        many=True,
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'bio',
            'avatar',
            'date_of_birth',
            'created_at',
            'updated_at',
            'friends',
            'sent_requests',
            'received_requests',
        ]


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
