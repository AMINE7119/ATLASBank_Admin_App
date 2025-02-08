import sys
import os

# Dynamically add the project root directory to sys.path
current_file_path = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(current_file_path, '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

import pandas as pd
from dal import insert_user, insert_account, insert_transaction
import csv
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging
import logging

setup_sql_logging()
sql_logger = logging.getLogger('sql_logger')

def extract_data(users_path, transactions_path):
    try:
        users_df = pd.read_csv(users_path, parse_dates=['date_of_birth', 'created_at'])
        transactions_df = pd.read_csv(transactions_path, parse_dates=['date'])
        return users_df, transactions_df
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None, None

def load_users_and_accounts(users_df):
    user_account_map = {}
    
    for _, row in users_df.iterrows():
        # Insert user
        user_id = insert_user(
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            phone=row['phone'],
            address=row['address'],
            date_of_birth=row['date_of_birth'],
            gender=row['gender'],
            job=row['job']
        )
        
        if user_id:
            # Insert accounts (20% of users get both types)
            account_type = 'savings' if _ % 5 == 0 else 'checking'
            account_number = insert_account(user_id, account_type)
            
            if account_number:
                user_account_map[user_id] = account_number
                if _ % 5 == 0:  # 20% get both accounts
                    second_account = insert_account(user_id, 'checking')
                    if second_account:
                        user_account_map[f"{user_id}_second"] = second_account
    
    return user_account_map

def load_transactions(transactions_df):
    success = True
    for _, row in transactions_df.iterrows():
        if not insert_transaction(
            account_id=row['account_id'],
            type=row['type'],
            amount=row['amount'],
            recipient_account=row['recipient_account'] if pd.notna(row['recipient_account']) else None,
            description=row['description'],
            date=row['date']
        ):
            success = False
    return success

def process_data(users_path, transactions_path):
    print("Starting ETL process...")
    
    users_df, transactions_df = extract_data(users_path, transactions_path)
    if users_df is None or transactions_df is None:
        return False
        
    print("Loading users and creating accounts...")
    user_account_map = load_users_and_accounts(users_df)
    
    print("Loading transactions...")
    success = load_transactions(transactions_df)
    
    return success

def load_users(csv_filepath):
    with open(csv_filepath, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            with get_cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO users 
                        (first_name, last_name, email, phone, address, date_of_birth, status, gender, job)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (row['first_name'], row['last_name'], row['email'], row['phone'], row['address'], row['date_of_birth'], True, row['gender'], row['job']))
                    sql_logger.info(f"Inserted user: {row['email']}")
                except Exception as e:
                    sql_logger.error(f"Error inserting user: {e}")

def load_transactions(csv_filepath):
    with open(csv_filepath, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            with get_cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO transactions 
                        (account_id, type, amount, recipient_account, description, date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (row['account_id'], row['type'], row['amount'], row['recipient_account'], row['description'], row['date']))
                    sql_logger.info(f"Inserted transaction for account ID: {row['account_id']}")
                except Exception as e:
                    sql_logger.error(f"Error inserting transaction: {e}")
