from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ChatViewSet

router = DefaultRouter()
router.register(r'chats', ChatViewSet, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
]
