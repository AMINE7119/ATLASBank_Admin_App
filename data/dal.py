import sys
import os

# Dynamically add the project root directory to sys.path
current_file_path = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(current_file_path, '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging
import logging

# Setup logging
setup_sql_logging()
sql_logger = logging.getLogger('sql_logger')

def insert_user(first_name, last_name, email, phone, address, date_of_birth, gender, job):
    with get_cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO users 
                (first_name, last_name, email, phone, address, date_of_birth, status, gender, job)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (first_name, last_name, email, phone, address, date_of_birth, True, gender, job))
            user_id = cur.fetchone()[0]
            sql_logger.info(f"Inserted user with ID: {user_id}")
            return user_id
        except Exception as e:
            sql_logger.error(f"Error inserting user: {e}")
            return None

def insert_account(user_id, type, balance=0):
    with get_cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO accounts 
                (user_id, type, balance, status)
                VALUES (%s, %s, %s, %s)
                RETURNING number
            """, (user_id, type, balance, True))
            account_number = cur.fetchone()[0]
            sql_logger.info(f"Inserted account with number: {account_number}")
            return account_number
        except Exception as e:
            sql_logger.error(f"Error inserting account: {e}")
            return None

def insert_transaction(account_id, type, amount, recipient_account=None, description=None, date=None):
    with get_cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO transactions 
                (account_id, type, amount, recipient_account, description, date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (account_id, type, amount, recipient_account, description, date))
            sql_logger.info(f"Inserted transaction for account ID: {account_id}")
            return True
        except Exception as e:
            sql_logger.error(f"Error inserting transaction: {e}")
            return False

if __name__ == "__main__":
    # Test insert_user
    user_id = insert_user(
        first_name='John',
        last_name='Doe',
        email='joe@atlasbank',
        phone='1234567890',
        address='123 Main St',
        date_of_birth='1990-01-01',
        gender='M',
        job='Software Engineer'
    )
    print(f"User inserted with ID: {user_id}")