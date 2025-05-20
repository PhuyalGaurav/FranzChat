from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.


class CustomUser(AbstractUser):
    # profile extensions
    bio = models.TextField(blank=True, default='')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # self-referential M2M to track accepted friendships
    friends = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='friend_set'
    )

    def __str__(self):
        return self.username

    def send_friend_request(self, to_user):
        # create a pending friend request if none exists
        if not FriendRequest.objects.filter(
            from_user=self, to_user=to_user, status='pending'
        ).exists():
            return FriendRequest.objects.create(from_user=self, to_user=to_user)
        return None

    def accept_friend_request(self, from_user):
        # accept a pending request and add each other to friends
        try:
            req = FriendRequest.objects.get(
                from_user=from_user, to_user=self, status='pending'
            )
        except FriendRequest.DoesNotExist:
            return None
        req.status = 'accepted'
        req.save()
        self.friends.add(from_user)
        from_user.friends.add(self)
        return req

    def reject_friend_request(self, from_user):
        # reject a pending request
        try:
            req = FriendRequest.objects.get(
                from_user=from_user, to_user=self, status='pending'
            )
        except FriendRequest.DoesNotExist:
            return None
        req.status = 'rejected'
        req.save()
        return req


class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_friend_requests',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_friend_requests',
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def accept(self):
        # accept request and add to both users' friend lists
        if self.status != 'pending':
            return
        self.status = 'accepted'
        self.save()
        self.from_user.friends.add(self.to_user)
        self.to_user.friends.add(self.from_user)

    def reject(self):
        if self.status != 'pending':
            return
        self.status = 'rejected'
        self.save()
