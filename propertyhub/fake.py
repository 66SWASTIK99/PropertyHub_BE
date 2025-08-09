from faker import Faker
import random

fake = Faker()

property_types = ["1BHK", "2BHK", "3BHK", "Studio"]
furnishings = ["furnished", "semi-furnished", "unfurnished"]

cities = [
    {"city": "Kathmandu", "areas": ["Thamel", "Baneshwor", "Lazimpat", "Koteshwor"]},
    {"city": "Pokhara", "areas": ["Lakeside", "Newroad", "Birauta", "Mahendrapul"]},
    {"city": "Lalitpur", "areas": ["Jawalakhel", "Patan", "Lagankhel", "Satdobato"]},
    {"city": "Bhaktapur", "areas": ["Suryabinayak", "Kamalbinayak", "Dattatreya", "Sallaghari"]},
]

def sql_escape(value):
    return value.replace("'", "''")

def generate_property():
    city_info = random.choice(cities)
    city = city_info["city"]
    area = random.choice(city_info["areas"])
    property_type = random.choice(property_types)
    furnishing = random.choice(furnishings)

    rent_min = random.randint(8000, 50000)
    rent_max = rent_min + random.randint(2000, 10000)
    area_sqft = random.randint(400, 1500)
    latitude = round(float(fake.latitude()), 6)
    longitude = round(float(fake.longitude()), 6)
    
    title = f"{property_type} in {area}, {city}"

    return f"""INSERT INTO properties (
        title, city, area, latitude, longitude,
        rent_min, rent_max, currency,
        property_type, area_sqft, furnishing
    ) VALUES (
        '{sql_escape(title)}', '{sql_escape(city)}', '{sql_escape(area)}', 
        {latitude}, {longitude},
        {rent_min}, {rent_max}, 'NPR',
        '{property_type}', {area_sqft}, '{furnishing}'
    );"""


for _ in range(50):
    print(generate_property())