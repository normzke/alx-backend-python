from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Prefetch
from .managers import UnreadMessagesManager

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    edited = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    thread_id = models.UUIDField(null=True, blank=True, help_text="ID of the root message in the thread")

    objects = models.Manager()
    unread = UnreadMessagesManager()

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

    def save(self, *args, **kwargs):
        if not self.thread_id and not self.parent_message:
            # This is a new thread
            import uuid
            self.thread_id = uuid.uuid4()
        elif self.parent_message and not self.thread_id:
            # This is a reply, inherit thread_id from parent
            self.thread_id = self.parent_message.thread_id
        super().save(*args, **kwargs)

    @classmethod
    def get_thread(cls, thread_id):
        """Get all messages in a thread with optimized queries"""
        return cls.objects.filter(thread_id=thread_id)\
            .select_related('sender', 'receiver')\
            .prefetch_related(
                Prefetch('replies',
                    queryset=cls.objects.select_related('sender', 'receiver')
                    .order_by('timestamp')
                )
            )\
            .order_by('timestamp')

    @classmethod
    def get_user_threads(cls, user):
        """Get all threads a user is part of"""
        return cls.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).filter(
            parent_message__isnull=True  # Only get root messages
        ).select_related('sender', 'receiver')\
         .prefetch_related(
             Prefetch('replies',
                 queryset=cls.objects.select_related('sender', 'receiver')
                 .order_by('timestamp')
             )
         )\
         .order_by('-timestamp')

    def get_reply_count(self):
        """Get the total number of replies in the thread"""
        return self.replies.count()

    def get_last_reply(self):
        """Get the most recent reply in the thread"""
        return self.replies.order_by('-timestamp').first()

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = 'Message histories'

    def __str__(self):
        return f"History for message {self.message.id} edited at {self.edited_at}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    created_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user} about message from {self.message.sender}" 