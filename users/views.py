from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import connection
from .services import signup_user_raw, login_user_raw
from .profile import edit_profile
from django.contrib.auth.hashers import make_password
from .exceptions import InvalidCredential, EmailAlreadyExists
from django.http import JsonResponse


@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup_view(request):
    username=request.data.get('username')
    email=request.data.get('email')
    password=request.data.get('password')
    
    if not username or not email or not password:
        return Response({"error": "All fields are required."}, status=400)
    
    try:
        result = signup_user_raw(request.data)
        return JsonResponse({
            "message": "Sign Up successful",
            "user_id": result["user_id"],
            # "refresh_token": result['refresh_token'],
            # "access_token": result['access_token'],
            # "expires_in": result['expires_in']
            }, status=200)
    
    except EmailAlreadyExists as e:
        return Response({"error": str(e)}, status=401)


@api_view(['POST'])
@permission_classes([AllowAny])       
def user_login_view(request):
    email=request.data.get('email')
    password=request.data.get('password')

    if not email or not password:
        return Response({"error": "All fields are required."}, status=400)

    try:
        result = login_user_raw(request.data)
        print("reached")
        return JsonResponse({
            "message": "Login successful",
            "user_id": result["user_id"],
            # "refresh_token": result['refresh_token'],
            # "access_token": result['access_token'],
            # "expires_in": result['expires_in']
            }, status=200)
    
    except InvalidCredential as e:
        return Response({"error": str(e)}, status=401)

    
class ForgetpwAPI(APIView):
    def post(self, request):
        password = request.data.get('password')
        email = request.data.get('email')
        hashed_password = make_password(password)
        conn = connection()
        cursor = conn.cursor()


        # Update the password
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", [hashed_password, email])
        conn.commit()
        conn.close()

        return Response({"message": "Password changed successfully"}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_profile_api(self, request):
        
    return edit_profile(request.data)
