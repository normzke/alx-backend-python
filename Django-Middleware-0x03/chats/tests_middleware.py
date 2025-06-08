from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.http import HttpResponse
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from .middleware import (
    RequestLoggingMiddleware,
    RestrictAccessByTimeMiddleware,
    OffensiveLanguageMiddleware,
    RolepermissionMiddleware
)

class RequestLoggingMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RequestLoggingMiddleware(get_response=lambda r: HttpResponse())

    def test_request_logging(self):
        request = self.factory.get('/chats/')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

class RestrictAccessByTimeMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RestrictAccessByTimeMiddleware(get_response=lambda r: HttpResponse())

    @patch('chats.middleware.datetime')
    def test_restricted_time_access(self, mock_datetime):
        # Set time to 22:00 (restricted time)
        mock_datetime.now.return_value = datetime(2024, 1, 1, 22, 0)
        request = self.factory.get('/chats/')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)

    @patch('chats.middleware.datetime')
    def test_allowed_time_access(self, mock_datetime):
        # Set time to 14:00 (allowed time)
        mock_datetime.now.return_value = datetime(2024, 1, 1, 14, 0)
        request = self.factory.get('/chats/')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

class OffensiveLanguageMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = OffensiveLanguageMiddleware(get_response=lambda r: HttpResponse())

    def test_rate_limiting(self):
        # Make multiple requests in quick succession
        for _ in range(6):  # Exceed the rate limit of 5 requests
            request = self.factory.post('/chats/')
            response = self.middleware(request)
        
        # The last request should be rate limited
        self.assertEqual(response.status_code, 403)

class RolepermissionMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RolepermissionMiddleware(get_response=lambda r: HttpResponse())
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )

    def test_restricted_action_regular_user(self):
        request = self.factory.delete('/chats/delete/1/')
        request.user = self.user
        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)

    def test_restricted_action_admin_user(self):
        request = self.factory.delete('/chats/delete/1/')
        request.user = self.admin_user
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_non_restricted_action(self):
        request = self.factory.get('/chats/')
        request.user = self.user
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200) 