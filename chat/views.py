from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Chat
from .serializers import ChatSerializer, ChatDetailSerializer, MessageSerializer

User = get_user_model()

# Create your views here.
class ChatViewSet(viewsets.ModelViewSet):
    """Create/list chats and view details with nested messages"""
    queryset = Chat.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatDetailSerializer
        return ChatSerializer

    def get_queryset(self):
        # only chats the user participates in
        return Chat.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        chat = serializer.save(creator_user=self.request.user)
        # add creator as participant and admin
        chat.participants.add(self.request.user)
        chat.admins.add(self.request.user)

    @action(detail=True, methods=['get', 'post'])
    def messages(self, request, slug=None):
        chat = self.get_object()
        if request.method == 'GET':
            msgs = chat.message_set.all()
            serializer = MessageSerializer(msgs, many=True)
            return Response(serializer.data)
        # POST: create new message
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, chat=chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
