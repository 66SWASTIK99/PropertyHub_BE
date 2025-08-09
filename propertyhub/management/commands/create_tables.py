from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Create tables using raw SQL for users, properties, requirements, and reviews."

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR(255),
                    email VARCHAR(255),
                    phone_number VARCHAR(20),
                    contact_details VARCHAR(255),
                    profile_photo TEXT,
                    user_type VARCHAR(50),
                    joined_date TIMESTAMP,
                    ratings FLOAT,
                    bio TEXT,
                    password VARCHAR(128)      
                );
                           
                CREATE TABLE IF NOT EXISTS lu_username2user_id(
                    lu_username VARCHAR(255),
                    lu_user_id INT
                );
                           
                CREATE INDEX idx_username ON lu_username2user_id(lu_username);
                           
                CREATE TABLE IF NOT EXISTS lu_email2user_id(
                    lu_email VARCHAR(255),
                    lu_user_id INT
                );
                           
                CREATE INDEX idx_email ON lu_email2user_id(lu_email);

                CREATE TABLE IF NOT EXISTS properties (
                    property_id SERIAL PRIMARY KEY,
                    title VARCHAR(255),
                    property_type VARCHAR(30),
                    contact_number VARCHAR(10),
                    location VARCHAR(150),
                    pincode VARCHAR(10),
                    monthly_rent DECIMAL(10, 2),
                    deposit_amount DECIMAL(10, 2),
                    photos TEXT,
                    property_description TEXT,
                    listed_date_time TIMESTAMP,
                    listed_by_user_id INT,
                    FOREIGN KEY (listed_by_user_id) REFERENCES users(user_id)
                );
                           
                CREATE TABLE IF NOT EXISTS user2property (
                    u2p_user_id INT,
                    u2p_property_id INT,
                    log_time TIMESTAMP,
                    FOREIGN KEY (u2p_user_id) REFERENCES users(user_id),
                    FOREIGN KEY (u2p_property_id) REFERENCES properties(property_id)
                );
                           
                CREATE INDEX idx_user_id_u2p ON user2property(u2p_user_id);

                CREATE TABLE IF NOT EXISTS requirements (
                    requirement_id SERIAL PRIMARY KEY,
                    user_id INT,
                    preferred_city VARCHAR(100),
                    property_type VARCHAR(100),
                    budget_min DECIMAL(10, 2),
                    budget_max DECIMAL(10, 2),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS reviews (
                    review_id SERIAL PRIMARY KEY,
                    reviewer_user_id INT,
                    reviewed_property_id INT,
                    rating INT CHECK (rating BETWEEN 0 AND 5),
                    review_text TEXT,
                    reviewed_date_time TIMESTAMP,
                    edited BOOLEAN,
                    FOREIGN KEY (reviewer_user_id) REFERENCES users(user_id),
                    FOREIGN KEY (reviewed_property_id) REFERENCES users(user_id)
                );
                           
                CREATE TABLE IF NOT EXISTS property2review (
                    p2r_user_id INT,
                    p2r_property_id INT,
                    log_time TIMESTAMP,
                    FOREIGN KEY (p2r_user_id) REFERENCES users(user_id),
                    FOREIGN KEY (p2r_property_id) REFERENCES properties(property_id)
                );
                
                CREATE INDEX idx_user_id_p2r ON property2review(p2r_user_id);
                           
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    token_hash CHAR(64) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    revoked BOOLEAN NOT NULL DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            """)

            cursor.execute("""
                CREATE OR REPLACE FUNCTION username2user_id_link_func()
                RETURNS TRIGGER AS $$
                BEGIN
                INSERT INTO lu_username2user_id (lu_username, lu_user_id)
                VALUES (NEW.username, NEW.user_id);
                RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                           
                CREATE TRIGGER username2user_id_link
                AFTER INSERT ON users
                FOR EACH ROW
                EXECUTE FUNCTION username2user_id_link_func();
            """)

            cursor.execute("""
                CREATE OR REPLACE FUNCTION user2propertylink_func()
                RETURNS trigger AS $$
                BEGIN
                INSERT INTO user2property (u2p_user_id, u2p_property_id, log_time)
                VALUES (NEW.listed_by_user_id, NEW.property_id, CURRENT_TIMESTAMP);
                RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                           
                CREATE TRIGGER user2propertylink
                AFTER INSERT ON properties
                FOR EACH ROW
                EXECUTE FUNCTION user2propertylink_func();
            """)

            cursor.execute("""
                CREATE OR REPLACE FUNCTION email2user_id_link_func()
                RETURNS trigger AS $$
                BEGIN
                INSERT INTO lu_email2user_id (lu_email, lu_user_id)
                VALUES (NEW.email, NEW.user_id);
                RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                           
                CREATE TRIGGER email2user_id_link
                AFTER INSERT ON users
                FOR EACH ROW
                EXECUTE FUNCTION email2user_id_link_func();
            """)

            cursor.execute("""
                CREATE OR REPLACE FUNCTION review2propertylink_func()
                RETURNS trigger AS $$
                BEGIN
                INSERT INTO property2review (p2r_user_id, p2r_property_id, log_time)
                VALUES (NEW.reviewer_user_id, NEW.reviewed_property_id, CURRENT_TIMESTAMP);
                RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                           
                CREATE TRIGGER review2propertylink
                AFTER INSERT ON reviews
                FOR EACH ROW
                EXECUTE FUNCTION review2propertylink_func();
            """)

            connection.commit()

        self.stdout.write(self.style.SUCCESS("All tables formed successfully using raw SQL."))