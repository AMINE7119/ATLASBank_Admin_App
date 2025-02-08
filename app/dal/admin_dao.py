import logging
from app.models.admin import Admin
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging

setup_sql_logging()
logger = logging.getLogger(__name__)

def get_admin_by_username(username):
    with get_cursor() as cursor:
        query = "SELECT * FROM admins WHERE username = %s"
        logger.info(query)
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        if row:
            return Admin(*row)
        return None