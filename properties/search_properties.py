from django.db import connection
from django.http import JsonResponse

def search_property(data):
    property_type = data.get('property_type')
    location = data.get('area_location')
    min_rent = data.get('min_rent')
    max_rent = data.get('max_rent')
    page = int(data.get('page', 0))  # default page 0
    offset = page * 15

    sql = """
        SELECT p.property_id, p.property_type, p.location, p.monthly_rent, 
               p.contact_number, p.property_description, p.listed_by_user_id, 
               u.username
        FROM properties p
        INNER JOIN users u ON p.listed_by_user_id = u.user_id
        WHERE p.property_type = %s 
          AND p.location = %s
          AND p.monthly_rent BETWEEN %s AND %s
        LIMIT 15 OFFSET %s
    """
    values = (property_type, location, min_rent, max_rent, offset)

    with connection.cursor() as cursor:
        cursor.execute(sql, values)
        rows = cursor.fetchall()

    data_out = [
        {
            'property_id': row[0],
            'property_type': row[1],
            'location': row[2],
            'rent': row[3],
            'contact_number': row[4],
            'property_description': row[5],
            'listed_by_user_id': row[6],
            'username': row[7]
        }
        for row in rows
    ]

    return JsonResponse(data_out, safe=False)


def search_property_by_userId(data):
    userId = data.get('userId')
    page = int(data.get('page', 0))
    offset = page * 15

    sql = """
        SELECT p.property_id, p.property_type, p.location, p.monthly_rent, 
               p.contact_number, p.property_description, u.username
        FROM user2property u2p
        INNER JOIN properties p ON u2p.u2p_property_id = p.property_id
        INNER JOIN users u ON p.listed_by_user_id = u.user_id
        WHERE u2p.u2p_userId = %s
        LIMIT 15 OFFSET %s
    """
    values = (userId, offset)

    with connection.cursor() as cursor:
        cursor.execute(sql, values)
        rows = cursor.fetchall()

    return JsonResponse([
        {
            'property_id': row[0],
            'property_type': row[1],
            'location': row[2],
            'rent': row[3],
            'contact_number': row[4],
            'property_description': row[5],
            'username': row[6]
        }
        for row in rows
    ], safe=False)
