from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import transaction
from .models import Message, Notification, MessageHistory

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """Create a notification when a new message is created"""
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )

@receiver(pre_save, sender=Message)
def log_message_history(sender, instance, **kwargs):
    """Log message history before saving an edited message"""
    if instance.pk:  # Only for existing messages
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                edited_by = getattr(instance, '_edited_by', None)
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=edited_by
                )
                instance.edited = True
                if edited_by:
                    instance.edited_by = edited_by
        except Message.DoesNotExist:
            pass

@receiver(post_delete, sender=User)
def delete_user_data(sender, instance, **kwargs):
    """Clean up user-related data when a user is deleted"""
    try:
        with transaction.atomic():
            # Delete all messages where user is sender or receiver
            Message.objects.filter(sender=instance).delete()
            Message.objects.filter(receiver=instance).delete()
            
            # Delete all notifications for the user
            Notification.objects.filter(user=instance).delete()
            
            # Delete all message histories for messages where user was sender or receiver
            MessageHistory.objects.filter(
                message__sender=instance
            ).delete()
            MessageHistory.objects.filter(
                message__receiver=instance
            ).delete()
    except Exception as e:
        # Log the error but don't prevent user deletion
        print(f"Error cleaning up user data: {str(e)}") 