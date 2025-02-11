import logging
from app.models.admin import Admin
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging

sql_logger = setup_sql_logging()

def get_admin_by_username(username):
    sql_logger = logging.getLogger('sql')
    with get_cursor() as cursor:
        query = "SELECT * FROM admins WHERE username = %s"
        sql_logger.info(f"Executing query: {query} with username: {username}")
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        if row:
            sql_logger.info(f"Found admin record for username: {username}")
            return Admin(*row)
        sql_logger.warning(f"No admin record found for username: {username}")
        return None