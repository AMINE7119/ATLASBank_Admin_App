from typing import Optional, Dict, Any
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging

class UserDAO:
    def __init__(self):
        self.sql_logger = setup_sql_logging()

    def create_user(self, data: Dict[str, Any]) -> Optional[int]:
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
            
            self.sql_logger.info(f"Creating new user: {values}")
            cursor.execute(query, values)
            return cursor.fetchone()[0]