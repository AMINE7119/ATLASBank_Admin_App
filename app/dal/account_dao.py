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
        with get_cursor() as cursor:
            try:
                cursor.execute("BEGIN")
                check_query = """
                    SELECT COUNT(*) FROM accounts 
                    WHERE user_id = %s AND type = %s
                """
                cursor.execute(check_query, (data['user_id'], data['type']))
                if cursor.fetchone()[0] > 0:
                    raise ValueError(f"User already has a {data['type']} account")
                insert_query = """
                    INSERT INTO accounts (user_id, type, balance, interest_rate, status)
                    VALUES (%s, %s, %s, %s, true)
                    RETURNING number;
                """
                values = (
                    data['user_id'],
                    data['type'],
                    data['balance'],
                    data.get('interest_rate', 0.00)
                )
                self.sql_logger.info(f"Creating new account with values: {values}")
                cursor.execute(insert_query, values)
                result = cursor.fetchone()
                if not result:
                    raise ValueError("Failed to get new account number")
                new_account_number = result[0]
                self.sql_logger.info(f"Created account with number: {new_account_number}")
                fetch_query = """
                    SELECT a.number, a.user_id, a.type, 
                           a.balance, a.status, a.interest_rate, a.created_at,
                           u.first_name, u.last_name, u.email
                    FROM accounts a
                    JOIN users u ON a.user_id = u.id
                    WHERE a.number = %s
                """
                cursor.execute(fetch_query, (new_account_number,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Could not fetch created account {new_account_number}")
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
                cursor.execute("COMMIT")
                self.sql_logger.info(f"Successfully created and fetched account {new_account_number}")
                return account
            except Exception as e:
                cursor.execute("ROLLBACK")
                self.sql_logger.error(f"Error creating account: {e}")
                raise

    def update_account(self, account_number: int, data: Dict[str, Any]) -> Optional[Account]:
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
        with get_cursor() as cursor:
            query = "DELETE FROM accounts WHERE number = %s"
            self.sql_logger.info(f"Executing query: {query} with account_number: {account_number}")
            cursor.execute(query, (account_number,))

    def search_accounts(self, search_term: str) -> List[Account]:
        with get_cursor() as cursor:
            try:
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
    
    def get_bank_statement(self, account_number: int, start_date: datetime = None, end_date: datetime = None) -> Dict:
        with get_cursor() as cursor:
            try:
                query = """
                    SELECT t.id, t.type, t.amount, t.recipient_account, 
                           t.description, t.date,
                           CASE 
                               WHEN t.type = 'DEPOSIT' THEN t.amount
                               WHEN t.type = 'TRANSFER' AND t.account_id = %s THEN -t.amount
                               WHEN t.type = 'TRANSFER' AND t.recipient_account = %s THEN t.amount
                               ELSE -t.amount
                           END as transaction_amount
                    FROM transactions t
                    WHERE (t.account_id = %s OR t.recipient_account = %s)
                """
                params = [account_number, account_number, account_number, account_number]
                if start_date:
                    query += " AND t.date >= %s"
                    params.append(start_date)
                if end_date:
                    query += " AND t.date <= %s"
                    params.append(end_date)
                query += " ORDER BY t.date"
                self.sql_logger.info(f"Executing bank statement query for account: {account_number}")
                cursor.execute(query, params)
                transactions = []
                running_balance = Decimal('0.00')
                for row in cursor.fetchall():
                    transaction_amount = Decimal(str(row[6]))
                    running_balance += transaction_amount
                    transactions.append({
                        'id': row[0],
                        'type': row[1],
                        'amount': abs(Decimal(str(row[2]))),
                        'recipient_account': row[3],
                        'description': row[4],
                        'date': row[5],
                        'transaction_amount': transaction_amount,
                        'running_balance': running_balance
                    })
                cursor.execute("SELECT balance FROM accounts WHERE number = %s", (account_number,))
                current_balance = cursor.fetchone()[0]
                statement = {
                    'account': self.get_account_by_number(account_number),
                    'transactions': transactions,
                    'start_date': start_date or transactions[0]['date'] if transactions else None,
                    'end_date': end_date or transactions[-1]['date'] if transactions else None,
                    'opening_balance': Decimal(str(current_balance)) - running_balance,
                    'closing_balance': Decimal(str(current_balance)),
                    'total_deposits': sum(t['transaction_amount'] for t in transactions if t['transaction_amount'] > 0),
                    'total_withdrawals': abs(sum(t['transaction_amount'] for t in transactions if t['transaction_amount'] < 0))
                }
                return statement
            except Exception as e:
                self.sql_logger.error(f"Error generating bank statement: {e}")
                raise
