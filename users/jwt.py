import jwt
import hashlib
from django.db import connection
from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
#import psycopg2


class TokenManager:
    #def __init__(self, db_connection):
        #self.connection = db_connection
    
    def generate_tokens(self, user_id):
        now = timezone.now()
        
        # Refresh token (longer expiry)
        refresh_payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': now + settings.BASE_JWT['REFRESH_TOKEN_LIFETIME'],
            'iat': now
        }
        
        # Access token (shorter expiry)
        access_payload = {
            'user_id': user_id,
            'type': 'access',
            'exp': now + settings.BASE_JWT['ACCESS_TOKEN_LIFETIME'],
            'iat': now
        }
        
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Storing refresh token in database for tracking/revocation
        self._store_refresh_token(user_id, refresh_token, refresh_payload['exp'])
        
        return {
            'refresh_token': refresh_token,
            'access_token': access_token,
            'expires_in': settings.BASE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        }
    
    def _store_refresh_token(self, user_id, token, expires_at):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
                VALUES (%s, %s, %s)
                """, (user_id, token_hash, expires_at))
        connection.commit()
    
    def verify_token(self, token, token_type="access"):
        
        # decoding token
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY,            
                algorithms=['HS256']            
            )

            if payload.get("type") != token_type:
                return None
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')

        user_id = payload["user_id"]        

        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", [user_id])
            row = cursor.fetchone()
        
        if not row:
            return None
        
        #user object
        user_data={
            "user_id" : row[0],
            "is_authenticated" : True
        }
        return user_data
        
        
    def refresh_access_token(self, refresh_token):
        # Verifying refresh token
        payload = self.verify_token(refresh_token, 'refresh')
        if not payload:
            return None
        
        # Checking if token is revoked
        if self._is_token_revoked(refresh_token):
            return None
        
        user_id = payload['user_id']
        
        # Generating new access token
        access_payload = {
            'user_id': user_id,
            'type': 'access',
            'exp': timezone.now() + settings.BASE_JWT['ACCESS_TOKEN_LIFETIME'],
            'iat': timezone.now()
        }
        
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
        
        return {
            'access_token': access_token,
            'expires_in': 3600
        }
    
    def _is_token_revoked(self, token):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT is_revoked FROM refresh_tokens 
                WHERE token_hash = %s AND expires_at > NOW()
                """, (token_hash,))
            result = cursor.fetchone()
        connection.commit()
        
        return result[0] if result else True  # Consider missing tokens as revoked
    
    def revoke_token(self, refresh_token):
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE refresh_tokens 
                SET is_revoked = TRUE 
                WHERE token_hash = %s
                """, (token_hash,))
        connection.commit()