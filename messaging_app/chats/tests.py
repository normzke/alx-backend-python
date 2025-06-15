from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Conversation, Message, MessageHistory, Notification
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ConversationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_conversation_creation(self):
        self.assertEqual(self.conversation.participants.count(), 2)
        self.assertIn(self.user1, self.conversation.participants.all())
        self.assertIn(self.user2, self.conversation.participants.all())

class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password123')
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user)
        self.message = Message.objects.create(conversation=self.conversation, sender=self.user, content='Hello, world!')

    def test_message_creation(self):
        self.assertEqual(self.message.sender, self.user)
        self.assertEqual(self.message.conversation, self.conversation)
        self.assertEqual(self.message.content, 'Hello, world!')

class ConversationAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password123')
        self.client.force_authenticate(user=self.user)
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user)

    def test_create_conversation(self):
        url = '/api/conversations/'
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 2)

    def test_list_conversations(self):
        url = '/api/conversations/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class MessageAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password123')
        self.client.force_authenticate(user=self.user)
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user)
        self.message = Message.objects.create(conversation=self.conversation, sender=self.user, content='Hello, world!')

    def test_create_message(self):
        url = '/api/messages/'
        data = {'conversation': self.conversation.id, 'content': 'New message'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 2)

    def test_list_messages(self):
        url = '/api/messages/?conversation=' + str(self.conversation.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class SignalTests(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        
        # Create a conversation
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_message_notification_creation(self):
        """Test that notifications are created when a new message is sent"""
        # Create a message
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="Test message"
        )
        
        # Check if notification was created for user2
        self.assertTrue(
            Notification.objects.filter(
                user=self.user2,
                message=message
            ).exists()
        )
        
        # Check that no notification was created for the sender
        self.assertFalse(
            Notification.objects.filter(
                user=self.user1,
                message=message
            ).exists()
        )

    def test_message_history_creation(self):
        """Test that message history is created when a message is edited"""
        # Create a message
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="Original message"
        )
        
        # Edit the message
        message.content = "Edited message"
        message.save()
        
        # Check if message history was created
        self.assertTrue(
            MessageHistory.objects.filter(
                message=message,
                content="Original message"
            ).exists()
        )
        
        # Check if edited flag was set
        message.refresh_from_db()
        self.assertTrue(message.edited)

    def test_user_deletion_cleanup(self):
        """Test that user-related data is cleaned up when a user is deleted"""
        # Create a message
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="Test message"
        )
        
        # Create a notification
        notification = Notification.objects.create(
            user=self.user2,
            message=message
        )
        
        # Delete user1
        self.user1.delete()
        
        # Check that user1's messages are deleted
        self.assertFalse(Message.objects.filter(sender=self.user1).exists())
        
        # Check that notifications for user2 still exist
        self.assertTrue(Notification.objects.filter(user=self.user2).exists())
        
        # Check that conversation still exists
        self.assertTrue(Conversation.objects.filter(id=self.conversation.id).exists())
