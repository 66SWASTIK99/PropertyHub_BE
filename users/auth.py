from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings
from .jwt import TokenManager  

class AuthenticatedUser:
    def __init__(self, user_id):
        self.user_id = user_id
        self.is_authenticated = True

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        #extracting token
        #checking "bearer "
        if not auth_header or not auth_header.startswith('Bearer '):
            raise exceptions.AuthenticationFailed('Missing or invalid Authorization header')
        
        # removing "bearer "
        token = auth_header[7:]

        token_manager = TokenManager()
        try:
            user = token_manager.verify_token(token)
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e))

        if not user:
            raise exceptions.AuthenticationFailed('User not found or token invalid')

        # DRF expects a (user, auth) tuple
        return (user)