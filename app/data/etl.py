import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
from dal import insert_user, insert_account, insert_transaction
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging
import logging

setup_sql_logging()
sql_logger = logging.getLogger('sql_logger')

def extract_data(users_path, accounts_path, transactions_path):
    try:
        users_df = pd.read_csv(users_path, parse_dates=['date_of_birth', 'created_at'])
        accounts_df = pd.read_csv(accounts_path, parse_dates=['created_at'])
        transactions_df = pd.read_csv(transactions_path, parse_dates=['date'])
        return users_df, accounts_df, transactions_df
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None, None, None

def load_users(users_df):
    users_loaded = 0
    for _, row in users_df.iterrows():
        user_id = insert_user(
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            phone=str(row['phone']),
            address=row['address'],
            date_of_birth=row['date_of_birth'],
            gender=row['gender'],
            job=row['job'],
            created_at=row['created_at']
        )
        if user_id:
            users_loaded += 1
    return users_loaded

def load_accounts(accounts_df):
    accounts_loaded = 0
    for _, row in accounts_df.iterrows():
        account_number = insert_account(
            user_id=row['user_id'],
            number=row['number'],
            type=row['type'],
            balance=row['balance'],
            status=row['status'],
            created_at=row['created_at'],
            interest_rate=row.get('interest_rate', 0)
        )
        if account_number:
            accounts_loaded += 1
    return accounts_loaded

def load_transactions(transactions_df):
    transactions_loaded = 0
    for _, row in transactions_df.iterrows():
        if insert_transaction(
            account_id=row['account_id'],
            type=row['type'],
            amount=row['amount'],
            recipient_account=row['recipient_account'],
            description=row['description'],
            date=row['date']
        ):
            transactions_loaded += 1
    return transactions_loaded

def process_data(users_path, accounts_path, transactions_path):
    print("Starting ETL process...")
    
    users_df, accounts_df, transactions_df = extract_data(
        users_path, accounts_path, transactions_path
    )
    
    if users_df is None or accounts_df is None or transactions_df is None:
        print("Failed to extract data.")
        return False
    
    print("Loading users...")
    users_loaded = load_users(users_df)
    print(f"Loaded {users_loaded} users")
    
    print("Loading accounts...")
    accounts_loaded = load_accounts(accounts_df)
    print(f"Loaded {accounts_loaded} accounts")
    
    print("Loading transactions...")
    transactions_loaded = load_transactions(transactions_df)
    print(f"Loaded {transactions_loaded} transactions")
    
    return users_loaded > 0 and accounts_loaded > 0 and transactions_loaded > 0

if __name__ == "__main__":
    # Set the paths to your CSV files
    users_path = r"C:\Users\AMINE\Desktop\github\ATLASBank_Admin_App\app\data\datasets\users.csv"
    accounts_path = r"C:\Users\AMINE\Desktop\github\ATLASBank_Admin_App\app\data\datasets\accounts.csv"
    transactions_path = r"C:\Users\AMINE\Desktop\github\ATLASBank_Admin_App\app\data\datasets\transactions.csv"
    
    # Process and load data
    success = process_data(users_path, accounts_path, transactions_path)
    
    if success:
        print("ETL process completed successfully.")
    else:
        print("ETL process encountered errors.")