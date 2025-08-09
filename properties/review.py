from django.db import connection
from rest_framework.response import Response

def edit_review(data, user_id):

    rating = data.get('rating')
    if not (rating>=0 or rating<=5):
        return Response({"error": "Rating not in specified range"}, status = 400)

    sql = """
    UPDATE reviews
    SET rating  = %s
    review text = %s
    edited = 1
    """
    values = (
        rating,
        data.get('review')
    )

    with connection.cursor() as cursor:
        cursor.execute(sql, values)
    connection.commit()

    return Response({"message": "Review edited successfully"}, status=201)