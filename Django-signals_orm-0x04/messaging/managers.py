from django.db import models

class UnreadMessagesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(read=False)

    def for_user(self, user):
        """Get unread messages for a specific user with optimized query"""
        return self.get_queryset().filter(receiver=user)\
            .select_related('sender')\
            .only(
                'id',
                'content',
                'timestamp',
                'sender__username',
                'sender__id',
                'read'
            )\
            .order_by('-timestamp')

    def mark_as_read(self, user, message_ids=None):
        """Mark messages as read for a user"""
        queryset = self.get_queryset().filter(receiver=user)
        if message_ids:
            queryset = queryset.filter(id__in=message_ids)
        return queryset.update(read=True)

    def get_unread_count(self, user):
        """Get count of unread messages for a user"""
        return self.get_queryset().filter(receiver=user).count() 