from typing import Optional
from app.models.user import User
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging

class UserDAO:
    def __init__(self):
        self.sql_logger = setup_sql_logging()

    def create_user(self, data) -> Optional[int]:
        """Create a new user and return the user ID"""
        with get_cursor() as cursor:
            query = """
                INSERT INTO users (first_name, last_name, email, phone, address, 
                                 date_of_birth, gender, job)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            values = (
                data['first_name'],
                data['last_name'],
                data['email'],
                data['phone'],
                data['address'],
                data['date_of_birth'],
                data['gender'],
                data.get('job')
            )
            
            self.sql_logger.info(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)
            user_id = cursor.fetchone()[0]
            return user_id