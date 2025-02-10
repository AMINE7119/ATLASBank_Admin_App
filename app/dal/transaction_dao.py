from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging

class TransactionDAO:
    def __init__(self):
        self.sql_logger = setup_sql_logging()

    def create_transaction(self, data: Dict[str, Any]) -> Optional[int]:
        with get_cursor() as cursor:
            query = """
                INSERT INTO transactions (account_id, type, amount, 
                                        recipient_account, description)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            values = (
                data['account_id'],
                data['type'],
                data['amount'],
                data.get('recipient_account'),
                data.get('description')
            )
            
            self.sql_logger.info(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)
            return cursor.fetchone()[0]

    def get_account_transactions(self, account_number: int) -> List[Dict]:
        with get_cursor() as cursor:
            query = """
                SELECT id, type, amount, recipient_account, description, date
                FROM transactions
                WHERE account_id = %s
                ORDER BY date DESC
            """
            self.sql_logger.info(f"Executing query: {query} with values: ({account_number},)")
            cursor.execute(query, (account_number,))
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    'id': row[0],
                    'type': row[1],
                    'amount': Decimal(str(row[2])),
                    'recipient_account': row[3],
                    'description': row[4],
                    'date': row[5]
                })
            return transactions

    def deposit(self, account_number: int, amount: Decimal, description: str = None) -> bool:
        with get_cursor() as cursor:
            try:
                cursor.execute("""
                    UPDATE accounts 
                    SET balance = balance + %s 
                    WHERE number = %s 
                    RETURNING balance""", 
                    (amount, account_number)
                )
                new_balance = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO transactions (account_id, type, amount, description)
                    VALUES (%s, 'DEPOSIT', %s, %s)""",
                    (account_number, amount, description)
                )
                
                self.sql_logger.info(f"Deposit processed: Account={account_number}, Amount={amount}, NewBalance={new_balance}")
                return True
                
            except Exception as e:
                self.sql_logger.error(f"Error processing deposit: {e}")
                raise

    def withdraw(self, account_number: int, amount: Decimal, description: str = None) -> bool:
        with get_cursor() as cursor:
            try:
                cursor.execute("SELECT balance FROM accounts WHERE number = %s", (account_number,))
                current_balance = cursor.fetchone()[0]
                
                if current_balance < amount:
                    raise ValueError("Insufficient funds")
                
                cursor.execute("""
                    UPDATE accounts 
                    SET balance = balance - %s 
                    WHERE number = %s 
                    RETURNING balance""", 
                    (amount, account_number)
                )
                new_balance = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO transactions (account_id, type, amount, description)
                    VALUES (%s, 'WITHDRAW', %s, %s)""",
                    (account_number, amount, description)
                )
                
                self.sql_logger.info(f"Withdrawal processed: Account={account_number}, Amount={amount}, NewBalance={new_balance}")
                return True
                
            except Exception as e:
                self.sql_logger.error(f"Error processing withdrawal: {e}")
                raise

    def transfer(self, from_account: int, to_account: int, amount: Decimal, description: str = None) -> bool:
        with get_cursor() as cursor:
            try:
                cursor.execute("SELECT balance FROM accounts WHERE number = %s", (from_account,))
                from_balance = cursor.fetchone()
                if not from_balance:
                    raise ValueError(f"Source account {from_account} not found")
                
                cursor.execute("SELECT number FROM accounts WHERE number = %s", (to_account,))
                if not cursor.fetchone():
                    raise ValueError(f"Destination account {to_account} not found")
                
                if from_balance[0] < amount:
                    raise ValueError("Insufficient funds")
                
                cursor.execute("""
                    UPDATE accounts SET balance = balance - %s WHERE number = %s;
                    UPDATE accounts SET balance = balance + %s WHERE number = %s;
                    """, 
                    (amount, from_account, amount, to_account)
                )
                
                cursor.execute("""
                    INSERT INTO transactions (account_id, type, amount, recipient_account, description)
                    VALUES (%s, 'TRANSFER', %s, %s, %s)""",
                    (from_account, amount, to_account, description)
                )
                
                self.sql_logger.info(f"Transfer processed: From={from_account}, To={to_account}, Amount={amount}")
                return True
                
            except Exception as e:
                self.sql_logger.error(f"Error processing transfer: {e}")
                raise

