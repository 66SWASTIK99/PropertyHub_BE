from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from .services import add_new_property_raw, add_review_raw
from .search_properties import search_property
from users.auth import JWTAuthentication
from django.http import JsonResponse
from django.db import connection

@api_view(['POST'])
@permission_classes([AllowAny])
def add_property_api(request):
        
        # jwt = JWTAuthentication()
        # token_payload = jwt.authenticate(request)
        
        # if token_payload is None:
        #     # Token is invalid or expired
        #     return Response({"error": "Invalid or expired token"}, status=401)
        
        # Extracting user_id from token payload
        # user_id = token_payload.get("user_id")

        data = request.data
        user_id = data.get('user_id')
        return add_new_property_raw(request.data, user_id)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review_api(self, request):
    jwt = JWTAuthentication()
    token_payload = jwt.authenticate(request)
        
    if token_payload is None:
        # Token is invalid or expired
        return Response({"error": "Invalid or expired token"}, status=401)
        
    # Extracting user_id from token payload
    user_id = token_payload.get("user_id")
    return add_review_raw(request.data, user_id)

@api_view(['POST'])
@permission_classes([AllowAny])
def search_properties_api(request):

        data = request.data
        
        return search_property(data)



def get_properties(request):
    sql = """
        SELECT * FROM
        (SELECT property_id, location, property_type, monthly_rent, contact_number, 
        property_description, listed_by_user_id, listed_date_time
        FROM properties
        ORDER BY listed_date_time DESC)
        INNER JOIN
        (SELECT username, user_id FROM users)
        ON listed_by_user_id = user_id
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    connection.commit()

    properties = []
    for row in rows:
        properties.append({
            "property_id": row[0],
            "area_location": row[1],
            "property_type": row[2],
            "rent": float(row[3]) if row[3] is not None else None,
            "contact_number": row[4],
            "description": row[5],
            "listed_by_user_id": row[6],
            "posted_at": row[7].isoformat() if row[6] else None,
            "listed_by_username": row[8]
        })

    return JsonResponse(properties, safe=False)