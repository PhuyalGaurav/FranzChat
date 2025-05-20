from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import UserViewSet, FriendRequestViewSet, FriendListView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'friend-requests', FriendRequestViewSet, basename='friendrequest')

urlpatterns = [
    path('friends/', FriendListView.as_view(), name='friend-list'),
    path('', include(router.urls)),
]
