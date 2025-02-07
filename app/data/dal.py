import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging
import logging

# Setup logging
setup_sql_logging()
sql_logger = logging.getLogger('sql_logger')

def insert_user(first_name, last_name, email, phone, address, date_of_birth, gender, job=None, created_at=None):
    with get_cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO users 
                (first_name, last_name, email, phone, address, date_of_birth, 
                 status, gender, job, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (first_name, last_name, email, phone, address, date_of_birth, 
                  True, gender, job, created_at))
            user_id = cur.fetchone()[0]
            sql_logger.info(f"Inserted user with ID: {user_id}")
            return user_id
        except Exception as e:
            sql_logger.error(f"Error inserting user: {e}")
            return None

def insert_account(user_id, type, balance, status, created_at, interest_rate=0):
    with get_cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO accounts 
                (user_id, type, balance, status, created_at, interest_rate)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING number
            """, (user_id, type, balance, status, created_at, interest_rate))
            
            account_number = cur.fetchone()[0]
            sql_logger.info(f"Inserted account with number: {account_number}")
            return account_number
        except Exception as e:
            sql_logger.error(f"Error inserting account: {e}")
            return None

def insert_transaction(account_id, type, amount, recipient_account=None, description=None, date=None):
    with get_cursor() as cur:
        try:
            # Ensure recipient_account is converted to None if it's NaN or an empty string
            recipient_account = recipient_account if recipient_account and str(recipient_account).strip() != 'nan' else None
            
            cur.execute("""
                INSERT INTO transactions 
                (account_id, type, amount, recipient_account, description, date)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (account_id, type, amount, recipient_account, description, date))
            
            transaction_id = cur.fetchone()[0]
            sql_logger.info(f"Inserted transaction with ID: {transaction_id}")
            return transaction_id
        except Exception as e:
            sql_logger.error(f"Error inserting transaction: {e}")
            return None

if __name__ == "__main__":
    # Test insert functions
    user_id = insert_user(
        first_name='John',
        last_name='Doe',
        email='4aJ8s@example.com',
        phone='1234567890',
        address='123 Main St',
        date_of_birth='1990-01-01',
        gender='M',
        job='Software Engineer',
        created_at='2022-01-01'
    )   
    print(f"User ID: {user_id}")
    
    account_number = insert_account(
        user_id=user_id,
        type='savings',
        balance=1000.00,
        status=True,
        created_at='2022-01-01',
        interest_rate=0.01
    )
    print(f"Account number: {account_number}")
    
    if account_number:
        transaction_id = insert_transaction(
            account_id=account_number, 
            type='DEPOSIT', 
            amount=500.00, 
            recipient_account=None, 
            description='Initial deposit', 
            date='2022-01-01'
        )
        print(f"Transaction ID: {transaction_id}")