from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Chat, Message

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'content',
            'timestamp',
            'is_read',
            'is_edited',
            'is_deleted_by_sender',
            'is_deleted_by_receiver',
        ]


class ChatSerializer(serializers.ModelSerializer):
    creator_user = serializers.ReadOnlyField(source='creator_user.username')
    participants = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True
    )
    admins = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Chat
        fields = [
            'id',
            'creator_user',
            'participants',
            'admins',
            'name',
            'slug',
            'is_group',
            'is_private',
            'timestamp',
        ]


class ChatDetailSerializer(ChatSerializer):
    """Extends ChatSerializer with nested messages"""
    messages = MessageSerializer(source='message_set', many=True, read_only=True)

    class Meta(ChatSerializer.Meta):
        fields = ChatSerializer.Meta.fields + ['messages']
