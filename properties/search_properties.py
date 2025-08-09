from django.db import connection
from rest_framework.response import Response
from django.http import JsonResponse
from datetime import datetime

def search_property(data):
    property_type = data.get('property_type')
    location = data.get('area_location')
    min_rent = data.get('min_rent')
    max_rent = data.get('max_rent')
    offset = 15
    # offset = (data.get('page'))*15
    
    sql = """
        SELECT * FROM
        (SELECT property_id, property_type, location, monthly_rent, contact_number, 
        property_description, listed_by_user_id 
        FROM properties 
        WHERE property_type = %s AND 
        location = %s AND
        monthly_rent BETWEEN %s AND %s
        LIMIT 15 OFFSET %s)
        INNER JOIN
        (SELECT username, user_id FROM users)
        ON listed_by_user_id = user_id
    """
    values = (
        property_type,
        location,
        min_rent,
        max_rent,
        offset
    )

    with connection.cursor() as cursor:
        cursor.execute(sql, values)
        rows = cursor.fetchall()
    connection.commit()

    data = [
        {'property_id': row[0], 
        'property_type': row[1],
        'location': row[2], 
        'rent': row[3],
        'contact_number': row[4],
        'property_description': row[5],
        'listed_by_user_id': row[6],
        'username': row[7]}
        for row in rows
    ]

    return JsonResponse(data)


def search_property_by_userId(data):
    userId = data.get('userId')
    offset = (data.get('page'))*15

    sql = """
        SELECT u2p_property_id FROM user2property
        WHERE u2p userId = %s
        LIMIT 15 OFFSET %s
    """
    values = (userId, offset)
    with connection.cursor() as cursor:
        cursor.execute(sql, values)
        rows = cursor.fetchall()
    connection.commit()
    
    return rows
