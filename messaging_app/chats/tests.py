from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

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
