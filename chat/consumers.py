import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Chat, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        # Check if user is authenticated and has access to this chat
        user = self.scope.get('user')
        if not user.is_authenticated:
            await self.close()
            return

        # Check if chat exists and user is participant
        chat_exists = await self.chat_exists(self.chat_id, user.id)
        if not chat_exists:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        user_id = self.scope['user'].id

        # Save message to database
        message_id = await self.save_message(user_id, self.chat_id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': user_id,
                'message_id': message_id,
                'timestamp': str(await self.get_message_timestamp(message_id))
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def chat_exists(self, chat_id, user_id):
        try:
            return Chat.objects.filter(id=chat_id, participants__id=user_id).exists()
        except Exception:
            return False

    @database_sync_to_async
    def save_message(self, user_id, chat_id, content):
        try:
            user = User.objects.get(id=user_id)
            chat = Chat.objects.get(id=chat_id)
            message = Message.objects.create(sender=user, chat=chat, content=content)
            return message.id
        except Exception as e:
            print(f"Error saving message: {str(e)}")
            return None

    @database_sync_to_async
    def get_message_timestamp(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            return message.timestamp
        except Exception:
            return None
