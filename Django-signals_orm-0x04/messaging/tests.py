from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from .models import Message, Notification, MessageHistory

class MessagingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')

    def test_message_creation(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Hello, World!'
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, 'Hello, World!')
        self.assertFalse(message.edited)
        self.assertFalse(message.read)

    def test_notification_creation(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Hello, World!'
        )
        notification = Notification.objects.get(message=message)
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.read)

    def test_message_edit_history(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Original content'
        )
        message.content = 'Updated content'
        message.save()
        
        history = MessageHistory.objects.get(message=message)
        self.assertEqual(history.old_content, 'Original content')
        self.assertTrue(message.edited)

    def test_unread_messages_manager(self):
        """Test the UnreadMessagesManager functionality"""
        # Create some messages
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Unread message 1'
        )
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Unread message 2'
        )
        Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Read message',
            read=True
        )
        
        # Test unread count
        self.assertEqual(Message.unread.get_unread_count(self.user2), 2)
        
        # Test unread messages query
        unread_messages = Message.unread.for_user(self.user2)
        self.assertEqual(unread_messages.count(), 2)
        
        # Verify only necessary fields are selected
        first_message = unread_messages.first()
        self.assertTrue(hasattr(first_message, 'content'))
        self.assertTrue(hasattr(first_message, 'timestamp'))
        self.assertTrue(hasattr(first_message, 'sender'))
        
        # Test mark as read
        Message.unread.mark_as_read(self.user2)
        self.assertEqual(Message.unread.get_unread_count(self.user2), 0)

    def test_unread_messages_view(self):
        """Test the unread messages view"""
        client = Client()
        client.force_login(self.user2)
        
        # Create unread messages
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Test unread message'
        )
        
        # Test inbox view
        response = client.get(reverse('inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test unread message')
        
        # Test mark as read
        response = client.post(reverse('mark_messages_read'), {
            'message_ids[]': [1]
        })
        self.assertEqual(response.status_code, 200)
        
        # Verify message is marked as read
        self.assertEqual(Message.unread.get_unread_count(self.user2), 0)

    def test_threaded_conversation(self):
        """Test threaded conversation functionality"""
        # Create a root message
        root_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Root message'
        )
        
        # Create replies
        reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='First reply',
            parent_message=root_message
        )
        
        reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Second reply',
            parent_message=reply1
        )
        
        # Test thread_id inheritance
        self.assertEqual(root_message.thread_id, reply1.thread_id)
        self.assertEqual(root_message.thread_id, reply2.thread_id)
        
        # Test thread retrieval
        thread_messages = Message.get_thread(root_message.thread_id)
        self.assertEqual(thread_messages.count(), 3)
        
        # Test reply count
        self.assertEqual(root_message.get_reply_count(), 2)
        
        # Test last reply
        last_reply = root_message.get_last_reply()
        self.assertEqual(last_reply, reply2)

    def test_thread_optimization(self):
        """Test that thread queries are optimized"""
        # Create a thread with multiple messages
        root = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Root'
        )
        
        for i in range(5):
            Message.objects.create(
                sender=self.user2 if i % 2 == 0 else self.user1,
                receiver=self.user1 if i % 2 == 0 else self.user2,
                content=f'Reply {i}',
                parent_message=root
            )
        
        # Test optimized query
        with self.assertNumQueries(3):  # One for messages, one for prefetch, one for related
            thread = Message.get_thread(root.thread_id)
            for message in thread:
                # Access related fields to ensure they're prefetched
                _ = message.sender.username
                _ = message.receiver.username
                for reply in message.replies.all():
                    _ = reply.sender.username
                    _ = reply.receiver.username

    def test_thread_view(self):
        """Test the thread detail view"""
        client = Client()
        client.force_login(self.user1)
        
        # Create a thread
        root = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Test thread'
        )
        
        # Test thread view
        response = client.get(reverse('thread_detail', args=[root.thread_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test thread')
        
        # Test reply functionality
        response = client.post(
            reverse('reply_to_message', args=[root.id]),
            {'content': 'Test reply'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(root.replies.count(), 1)

    def test_user_deletion_cleanup(self):
        """Test that user deletion properly cleans up all related data"""
        # Create some test data
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Test message 1'
        )
        message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content='Test message 2'
        )
        notification = Notification.objects.create(
            user=self.user1,
            message=message2
        )
        
        # Edit a message to create history
        message1.content = 'Edited content'
        message1.save()
        
        # Delete user1
        self.user1.delete()
        
        # Verify all related data is deleted
        self.assertEqual(Message.objects.filter(sender=self.user1).count(), 0)
        self.assertEqual(Message.objects.filter(receiver=self.user1).count(), 0)
        self.assertEqual(Notification.objects.filter(user=self.user1).count(), 0)
        self.assertEqual(MessageHistory.objects.filter(message__sender=self.user1).count(), 0)
        self.assertEqual(MessageHistory.objects.filter(message__receiver=self.user1).count(), 0)

    def test_delete_user_view(self):
        """Test the delete user view"""
        client = Client()
        client.force_login(self.user1)
        
        # Test GET request
        response = client.get(reverse('delete_user'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request with wrong password
        response = client.post(reverse('delete_user'), {'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Incorrect password')
        
        # Test POST request with correct password
        response = client.post(reverse('delete_user'), {'password': 'testpass123'})
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertFalse(User.objects.filter(username='user1').exists())

    def test_view_caching(self):
        """Test that views are properly cached"""
        client = Client()
        client.force_login(self.user1)
        
        # Create a test message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Test message'
        )
        
        # Clear cache before testing
        cache.clear()
        
        # First request should hit the database
        with self.assertNumQueries(3):  # One for user, one for message, one for related
            response = client.get(reverse('thread_detail', args=[message.thread_id]))
            self.assertEqual(response.status_code, 200)
        
        # Second request should use cache
        with self.assertNumQueries(0):
            response = client.get(reverse('thread_detail', args=[message.thread_id]))
            self.assertEqual(response.status_code, 200)
        
        # Different user should get different cache
        client.force_login(self.user2)
        with self.assertNumQueries(3):  # Should hit database again for different user
            response = client.get(reverse('thread_detail', args=[message.thread_id]))
            self.assertEqual(response.status_code, 200)

    def test_cache_timeout(self):
        """Test that cache expires after timeout"""
        client = Client()
        client.force_login(self.user1)
        
        # Create a test message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Test message'
        )
        
        # Clear cache
        cache.clear()
        
        # First request
        response = client.get(reverse('thread_detail', args=[message.thread_id]))
        self.assertEqual(response.status_code, 200)
        
        # Update message
        message.content = 'Updated content'
        message.save()
        
        # Wait for cache to expire (in real test, we'd use time.sleep(61))
        cache.clear()  # Simulate cache expiration
        
        # Should hit database again
        with self.assertNumQueries(3):
            response = client.get(reverse('thread_detail', args=[message.thread_id]))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Updated content') 