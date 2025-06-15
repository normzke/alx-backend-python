from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message, MessageHistory, Notification, Conversation

User = get_user_model()

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal to create a notification when a new message is created.
    Creates notifications for all participants in the conversation except the sender.
    """
    if created:
        conversation = instance.conversation
        for participant in conversation.participants.all():
            if participant != instance.sender:
                Notification.objects.create(
                    user=participant,
                    message=instance
                )

@receiver(pre_save, sender=Message)
def log_message_history(sender, instance, **kwargs):
    """
    Signal to log message history before a message is edited.
    """
    if instance.pk:  # Only for existing messages
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                MessageHistory.objects.create(
                    message=instance,
                    content=old_message.content
                )
                instance.edited = True
        except Message.DoesNotExist:
            pass

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal to clean up user-related data when a user is deleted.
    """
    # Delete all notifications for the user
    Notification.objects.filter(user=instance).delete()
    
    # Delete all messages sent by the user
    Message.objects.filter(sender=instance).delete()
    
    # Delete all conversations where the user was the only participant
    for conversation in Conversation.objects.filter(participants=instance):
        if conversation.participants.count() <= 1:
            conversation.delete() 