from django.db import connection
from .exceptions import InvalidCredential, UserAlreadyExists, EmailAlreadyExists
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .jwt import TokenManager

def login_user_raw(user_data):
    email = user_data.get("email")
    password  = user_data.get("password")

    with connection.cursor() as cursor:
        cursor.execute("SELECT user_id, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

    if not user:
        raise InvalidCredential("Invalid credentials")

    user_id, stored_hashed_password = user

    if not check_password(password, stored_hashed_password):
        raise InvalidCredential("Invalid credentials")

    # Password is correct
            
    # Generating tokens
    token_manager = TokenManager()
    tokens = token_manager.generate_tokens(user_id)
            
    return{
            "message": "Login successful",
            "user_id": user_id,
            # "user_id": tokens["user_id"],
            # "refresh_token": tokens['refresh_token'],
            # "access_token": tokens['access_token'],
            # "expires_in": tokens['expires_in']
            }
     
        

def signup_user_raw(user_data):
    email = user_data.get("email")
    username = user_data.get("username")
    password = user_data.get("password")

    if not email or not username or not password:
        raise ValueError("Missing required fields.")

    # Checking for existing email
    with connection.cursor() as cursor:
        cursor.execute("SELECT email FROM users WHERE email = %s", [email])
        if cursor.fetchone():
            raise EmailAlreadyExists("Email already exists.")

    # Hash password
    hashed_password = make_password(password)

    # User Insertion
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
            RETURNING user_id
        """, (username, email, hashed_password))
        user_id = cursor.fetchone()[0]

    connection.commit()

    # Token generation
    token_manager = TokenManager()
    tokens = token_manager.generate_tokens(user_id)

    return {
        "user_id": user_id,
        "refresh_token": tokens["refresh_token"],
        "access_token": tokens["access_token"],
        "expires_in": tokens["expires_in"]
    }

def get_user_profile_raw(user_id):
    sql = """
        SELECT id, username, email, contact_number, bio 
        FROM auth_user WHERE id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, user_id)
        row = cursor.fetchone()
    connection.commit()

    if row:
        return {
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'contact_number': row[3],
            'bio': row[4]
        }
    return None