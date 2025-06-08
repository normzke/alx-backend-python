from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication class that extends the default JWTAuthentication
    to add additional functionality if needed.
    """
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception as e:
            raise AuthenticationFailed('Invalid token or token expired')

class CustomBasicAuthentication(BaseAuthentication):
    """
    Custom Basic Authentication class that extends the default BasicAuthentication
    to add additional functionality if needed.
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Basic '):
            return None

        try:
            # Decode the base64 encoded credentials
            import base64
            auth_decoded = base64.b64decode(auth_header.split(' ')[1]).decode('utf-8')
            username, password = auth_decoded.split(':')
            
            # Authenticate the user
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise AuthenticationFailed('Invalid credentials')
                
            return (user, None)
        except Exception as e:
            raise AuthenticationFailed('Invalid credentials') 