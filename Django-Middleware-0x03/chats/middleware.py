import logging
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden
from collections import defaultdict

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Configure logging
        logging.basicConfig(
            filename='requests.log',
            level=logging.INFO,
            format='%(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        # Get user information
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        
        # Log the request information
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        
        # Process the request
        response = self.get_response(request)
        
        return response

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        
        # Check if the request is for the chat endpoints
        if 'chats' in request.path:
            # Restrict access between 9 PM (21:00) and 6 AM (06:00)
            if current_hour >= 21 or current_hour < 6:
                return HttpResponseForbidden(
                    "Access to chat is restricted between 9 PM and 6 AM. "
                    "Please try again during allowed hours."
                )
        
        # Process the request if time is allowed
        response = self.get_response(request)
        return response

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to store request counts per IP
        self.request_counts = defaultdict(list)
        # Maximum number of requests allowed per time window
        self.max_requests = 5
        # Time window in seconds (1 minute)
        self.time_window = 60

    def __call__(self, request):
        # Only apply rate limiting to POST requests to chat endpoints
        if request.method == 'POST' and 'chats' in request.path:
            # Get client IP address
            ip_address = self.get_client_ip(request)
            current_time = datetime.now()

            # Clean up old requests outside the time window
            self.request_counts[ip_address] = [
                req_time for req_time in self.request_counts[ip_address]
                if current_time - req_time < timedelta(seconds=self.time_window)
            ]

            # Check if the user has exceeded the rate limit
            if len(self.request_counts[ip_address]) >= self.max_requests:
                return HttpResponseForbidden(
                    "Rate limit exceeded. Please wait before sending more messages."
                )

            # Add current request to the count
            self.request_counts[ip_address].append(current_time)

        # Process the request
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define restricted actions that require admin/moderator role
        self.restricted_actions = {
            'DELETE': ['delete', 'remove', 'ban'],
            'PUT': ['update', 'modify'],
            'POST': ['create', 'add']
        }

    def __call__(self, request):
        # Check if the request is for chat endpoints
        if 'chats' in request.path:
            # Get the user from the request
            user = request.user

            # Check if user is authenticated
            if not user.is_authenticated:
                return HttpResponseForbidden(
                    "Authentication required to access this resource."
                )

            # Check if the request method and path indicate a restricted action
            method = request.method
            path = request.path.lower()

            # Check if this is a restricted action
            is_restricted = any(
                action in path for action in self.restricted_actions.get(method, [])
            )

            # If it's a restricted action, check user role
            if is_restricted:
                # Check if user is admin or moderator
                if not (user.is_staff or user.is_superuser):
                    return HttpResponseForbidden(
                        "You don't have permission to perform this action. "
                        "Only administrators and moderators are allowed."
                    )

        # Process the request
        response = self.get_response(request)
        return response 