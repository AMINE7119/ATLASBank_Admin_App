from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.models.account import Account
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging

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
            
            accounts = []
            for row in cursor.fetchall():
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
    
    def create_account(self, data: Dict[str, Any]) -> Optional[Account]:
        """Create a new account"""
        with get_cursor() as cursor:
            try:
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
                result = cursor.fetchone()
                
                if result:
                    account_number, created_at = result
                    return self.get_account_by_number(account_number)
                return None
                    
            except Exception as e:
                self.sql_logger.error(f"Error creating account: {e}")
                raise

    def update_account(self, account_number: int, data: Dict[str, Any]) -> Optional[Account]:
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

    def search_accounts(self, search_term: str) -> List[Account]:
        """Search accounts by first name, last name, or account number"""
        with get_cursor() as cursor:
            try:
                # Try to convert search term to number for account number search
                try:
                    account_number = int(search_term)
                    number_search = True
                except ValueError:
                    number_search = False

                if number_search:
                    query = """
                        SELECT a.number, a.user_id, a.type, 
                               a.balance, a.status, a.interest_rate, a.created_at,
                               u.first_name, u.last_name, u.email
                        FROM accounts a
                        JOIN users u ON a.user_id = u.id
                        WHERE a.number = %s
                    """
                    params = (account_number,)
                else:
                    query = """
                        SELECT a.number, a.user_id, a.type, 
                               a.balance, a.status, a.interest_rate, a.created_at,
                               u.first_name, u.last_name, u.email
                        FROM accounts a
                        JOIN users u ON a.user_id = u.id
                        WHERE LOWER(u.first_name) LIKE LOWER(%s) 
                        OR LOWER(u.last_name) LIKE LOWER(%s)
                    """
                    search_pattern = f"%{search_term}%"
                    params = (search_pattern, search_pattern)

                self.sql_logger.info(f"Executing search query with term: {search_term}")
                cursor.execute(query, params)
                accounts = []
                
                for row in cursor.fetchall():
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
                    accounts.append(account)
                
                return accounts
                
            except Exception as e:
                self.sql_logger.error(f"Database error during search: {str(e)}")
                raise