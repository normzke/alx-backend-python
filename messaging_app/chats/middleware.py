import logging
from datetime import datetime

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
        
        # Log the request
        self.logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")
        
        # Process the request
        response = self.get_response(request)
        
        return response 