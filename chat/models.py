from django.db import models
from users.models import CustomUser as User

class Chat(models.Model):
    creator_user = models.ForeignKey(User, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='chat_participants')
    admins = models.ManyToManyField(User, related_name='chat_admins')
    name = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_group = models.BooleanField(default=False)
    is_private = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, unique=True)

    @property
    def is_admin(self):
        """
        Check if the user is an admin of the chat.
        """
        return self.admins.filter(id=self.creator_user.id).exists()

    @property
    def is_participant(self):
        """
        Check if the user is a participant of the chat.
        """
        return self.participants.filter(id=self.creator_user.id).exists()

    @property
    def is_private_chat(self):
        """
        Check if the chat is private.
        """
        return self.is_private
    @property
    def is_group_chat(self):
        """
        Check if the chat is a group chat.
        """
        return self.is_group

    def slugify(self):
        """
        Generate a unique slug for the chat based on its name and creator.
        """
        from django.utils.text import slugify
        from django.utils.crypto import get_random_string

        base_slug = slugify(self.name)
        unique_slug = f"{base_slug}-{get_random_string(6)}"
        return unique_slug

    def save(self, *args, **kwargs):
        """
        Override the save method to set the slug before saving the instance.
        """
        if not self.slug:
            self.slug = self.slugify()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Chat: {self.name} (ID: {self.id})"

    def __repr__(self):
        return f"Chat(creator_user={self.creator_user}, participants={self.participants}, admins={self.admins}, name={self.name}, message={self.message}, timestamp={self.timestamp}, is_group={self.is_group}, is_private={self.is_private}, slug={self.slug})"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted_by_sender = models.BooleanField(default=False)
    is_deleted_by_receiver = models.BooleanField(default=False)
    
    def mark_as_read(self):
        """
        Mark the message as read.
        """
        self.is_read = True
        self.save()

    def __str__(self):
        return f"Message from {self.sender} in {self.chat} at {self.timestamp}"


