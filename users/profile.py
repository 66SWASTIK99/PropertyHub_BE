from django.db import connection
from rest_framework.response import Response

def edit_profile(data, user_id):
    
    sql = """
        UPDATE users
        SET username = %s, 
        email = %s, 
        phone_number = %s,
        bio = %s)
        WHERE user_id = %s
    """
    values = (
        data.get('username'),
        data.get('email'),
        data.get('phone_number'),
        data.get('bio'),
        user_id
    )

    with connection.cursor() as cursor:
        cursor.execute(sql, values)
    connection.commit()
    
    return Response({"message": "profile updated successfully"}, status = 201)


def search_profile(data, user_id):

    sql = """
        SELECT user_id, email, phone_number, ratings
        FROM
        (SELECT user_id FROM lu_username2user_id
        WHERE username ILIKE '%s%';) AS L
        INNER JOIN 
        users
        L.user_id = users.user_id
    """

    values = (data.get('name'))

    with connection.cursor() as cursor:
        cursor.execute(sql, values)
        rows = cursor.fetchall()
    
    connection.commit()

    return rows

def get_user_image(request, user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT image_path FROM user_profile WHERE id = %s", [user_id])
        row = cursor.fetchone()

    if row:
        image_url = request.build_absolute_uri(f'/{row[0]}')  # Convert to full URL
        return Response({'image_url': image_url})
    else:
        return Response({'error': 'User not found'}, status=404)