from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging

class TransactionDAO:
    def __init__(self):
        self.sql_logger = setup_sql_logging()

    def create_transaction(self, data: Dict[str, Any]) -> Optional[int]:
        """Create a new transaction"""
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
        """Get all transactions for an account"""
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
        """Process a deposit transaction"""
        with get_cursor() as cursor:
            try:
                # Update account balance
                cursor.execute("""
                    UPDATE accounts 
                    SET balance = balance + %s 
                    WHERE number = %s 
                    RETURNING balance""", 
                    (amount, account_number)
                )
                new_balance = cursor.fetchone()[0]
                
                # Create transaction record
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
        """Process a withdrawal transaction"""
        with get_cursor() as cursor:
            try:
                # Check sufficient balance
                cursor.execute("SELECT balance FROM accounts WHERE number = %s", (account_number,))
                current_balance = cursor.fetchone()[0]
                
                if current_balance < amount:
                    raise ValueError("Insufficient funds")
                
                # Update account balance
                cursor.execute("""
                    UPDATE accounts 
                    SET balance = balance - %s 
                    WHERE number = %s 
                    RETURNING balance""", 
                    (amount, account_number)
                )
                new_balance = cursor.fetchone()[0]
                
                # Create transaction record
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
        """Process a transfer between accounts"""
        with get_cursor() as cursor:
            try:
                # Verify accounts exist
                cursor.execute("SELECT balance FROM accounts WHERE number = %s", (from_account,))
                from_balance = cursor.fetchone()
                if not from_balance:
                    raise ValueError(f"Source account {from_account} not found")
                
                cursor.execute("SELECT number FROM accounts WHERE number = %s", (to_account,))
                if not cursor.fetchone():
                    raise ValueError(f"Destination account {to_account} not found")
                
                # Check sufficient balance
                if from_balance[0] < amount:
                    raise ValueError("Insufficient funds")
                
                # Update both accounts
                cursor.execute("""
                    UPDATE accounts SET balance = balance - %s WHERE number = %s;
                    UPDATE accounts SET balance = balance + %s WHERE number = %s;
                    """, 
                    (amount, from_account, amount, to_account)
                )
                
                # Create transaction record
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

    # Continuation of TransactionDAO class in transaction_dao.py
    def get_bank_statement(self, account_number: int, start_date: datetime = None, end_date: datetime = None) -> Dict:
       """Get bank statement for an account with optional date range"""
       with get_cursor() as cursor:
           try:
               # Build transaction query
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

               # Get current account balance
               cursor.execute("SELECT balance FROM accounts WHERE number = %s", (account_number,))
               current_balance = cursor.fetchone()[0]

               statement = {
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