# app/dal/account_dao.py
from typing import List, Optional, Dict, Any
from app.models.account import Account
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging
from decimal import Decimal
from datetime import datetime

class AccountDAO:
    def __init__(self):
        self.sql_logger = setup_sql_logging()

    def get_all_accounts(self) -> List[Account]:
        """Fetch all accounts with basic user information"""
        with get_cursor() as cursor:
            query = """
                SELECT a.number, a.user_id, a.type, 
                       a.balance, a.status, a.interest_rate, a.created_at,
                       u.first_name, u.last_name, u.email
                FROM accounts a
                JOIN users u ON a.user_id = u.id
                ORDER BY a.number
            """
            self.sql_logger.info(f"Executing query: {query}")
            cursor.execute(query)
            rows = cursor.fetchall()
            accounts = []
            for row in rows:
                account = Account(
                    account_number=row[0],
                    user_id=row[1],
                    account_type=row[2],
                    balance=Decimal(str(row[3])),
                    is_active=row[4],
                    interest_rate=Decimal(str(row[5])) if row[5] else Decimal('0.00'),
                    created_at=row[6]
                )
                # Add user information
                account.holder_name = f"{row[7]} {row[8]}"
                account.holder_email = row[9]
                accounts.append(account)
            return accounts

    def get_account_by_number(self, account_number: int) -> Optional[Account]:
        """Fetch a specific account by its number with user information"""
        with get_cursor() as cursor:
            query = """
                SELECT a.number, a.user_id, a.type, 
                       a.balance, a.status, a.interest_rate, a.created_at,
                       u.first_name, u.last_name, u.email
                FROM accounts a
                JOIN users u ON a.user_id = u.id
                WHERE a.number = %s
            """
            self.sql_logger.info(f"Executing query: {query} with account_number: {account_number}")
            cursor.execute(query, (account_number,))
            row = cursor.fetchone()
            if row:
                account = Account(
                    account_number=row[0],
                    user_id=row[1],
                    account_type=row[2],
                    balance=Decimal(str(row[3])),
                    is_active=row[4],
                    interest_rate=Decimal(str(row[5])) if row[5] else Decimal('0.00'),
                    created_at=row[6]
                )
                account.holder_name = f"{row[7]} {row[8]}"
                account.holder_email = row[9]
                return account
            return None

    def create_account(self, data: Dict[str, Any]) -> Account:
        """Create a new account"""
        with get_cursor() as cursor:
            query = """
                INSERT INTO accounts (user_id, type, balance, interest_rate)
                VALUES (%s, %s, %s, %s)
                RETURNING number, created_at
            """
            values = (
                data['user_id'],
                data['type'],
                data['balance'],
                data.get('interest_rate', 0.00)
            )
            self.sql_logger.info(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)
            account_number, created_at = cursor.fetchone()
            return self.get_account_by_number(account_number)

    def update_account(self, account_number: int, data: Dict[str, Any]) -> Account:
        """Update an existing account"""
        with get_cursor() as cursor:
            query = """
                UPDATE accounts
                SET type = %s,
                    balance = %s,
                    status = %s,
                    interest_rate = %s
                WHERE number = %s
            """
            values = (
                data['type'],
                data['balance'],
                data.get('status', True),
                data.get('interest_rate', 0.00),
                account_number
            )
            self.sql_logger.info(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)
            return self.get_account_by_number(account_number)

    def delete_account(self, account_number: int) -> None:
        """Delete an account"""
        with get_cursor() as cursor:
            query = "DELETE FROM accounts WHERE number = %s"
            self.sql_logger.info(f"Executing query: {query} with account_number: {account_number}")
            cursor.execute(query, (account_number,))