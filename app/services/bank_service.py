# app/services/bank_service.py
from typing import List, Optional, Dict, Any
from flask import session
from werkzeug.exceptions import NotFound, Forbidden, Unauthorized
from app.models.account import Account
from app.dal.user_dao import UserDAO
from app.dal.transaction_dao import TransactionDAO
from app.dal.account_dao import AccountDAO
from app.logger.app_logging import setup_logging
from functools import wraps
from decimal import Decimal
from datetime import datetime
from decimal import Decimal
from datetime import datetime
import decimal

logger = setup_logging()

class BankService:
    def __init__(self):
        self.account_dao = AccountDAO()
        self.transaction_dao = TransactionDAO()
        self.user_dao = UserDAO()

    def check_auth(self, f, *args, **kwargs):
        """Handle authentication and authorization"""
        if not session.get('admin_id'):
            logger.warning(f"Unauthorized access attempt to {f.__name__}")
            raise Unauthorized("Authentication required")
        return f(*args, **kwargs)

    def list_accounts(self) -> List[Account]:
        """Get all accounts with related information"""
        try:
            logger.info("Fetching all accounts")
            accounts = self.account_dao.get_all_accounts()
            #append by balance 
            accounts.sort(key=lambda x: x.balance, reverse=True)
            logger.info(f"Successfully fetched {len(accounts)} accounts")
            return accounts
        except Exception as e:
            logger.error(f"Error fetching accounts: {str(e)}")
            raise

    def get_account(self, account_number: int) -> Account:
        """Get single account with full details"""
        try:
            logger.info(f"Fetching account {account_number}")
            account = self.account_dao.get_account_by_number(account_number)
            if not account:
                logger.warning(f"Account {account_number} not found")
                raise NotFound(f"Account {account_number} not found")
            return account
        except Exception as e:
            logger.error(f"Error fetching account {account_number}: {str(e)}")
            raise

    def update_account(self, account_number: int, data: Dict[str, Any]) -> Account:
        """Update account details"""
        try:
            logger.info(f"Updating account {account_number}")
            if not self._check_edit_permission(account_number):
                raise Forbidden("You don't have permission to edit this account")
            
            account = self.account_dao.get_account_by_number(account_number)
            if not account:
                raise NotFound(f"Account {account_number} not found")

            # Validate and convert data
            update_data = {
                'type': data['type'],
                'balance': Decimal(str(data['balance'])),
                'status': bool(data.get('status', True)),
                'interest_rate': Decimal(str(data.get('interest_rate', 0.00)))
            }

            updated_account = self.account_dao.update_account(account_number, update_data)
            logger.info(f"Successfully updated account {account_number}")
            return updated_account
        except Exception as e:
            logger.error(f"Error updating account {account_number}: {str(e)}")
            raise

    def create_account(self, data: Dict[str, Any]) -> Account:
        """Create new user and account"""
        try:
            logger.info("Creating new user and account")
            
            # Validate required user fields
            required_user_fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'date_of_birth', 'gender']
            missing_fields = [field for field in required_user_fields if not data.get(field)]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            # Validate required account fields
            if not data.get('type'):
                raise ValueError("Account type is required")
            if data['type'] not in ['savings', 'checking']:
                raise ValueError("Invalid account type. Must be 'savings' or 'checking'")

            # Convert and validate numeric fields
            try:
                balance = Decimal(str(data.get('balance', '0')))
                interest_rate = Decimal(str(data.get('interest_rate', '0.00')))
                
                if balance < 0:
                    raise ValueError("Balance cannot be negative")
                if interest_rate < 0 or interest_rate > 100:
                    raise ValueError("Interest rate must be between 0 and 100")
            except (ValueError, TypeError, decimal.InvalidOperation):
                raise ValueError("Invalid numeric values provided for balance or interest rate")

            # Prepare user data
            user_data = {
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email'],
                'phone': data['phone'],
                'address': data['address'],
                'date_of_birth': datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
                'gender': data['gender'],
                'job': data.get('job')
            }
            
            # Create user
            try:
                user_id = self.user_dao.create_user(user_data)
                if not user_id:
                    raise ValueError("Failed to create user")
                logger.info(f"Created user with ID: {user_id}")
            except Exception as e:
                if 'duplicate key' in str(e).lower():
                    raise ValueError("A user with this email or phone already exists")
                raise
            
            # Prepare account data
            account_data = {
                'user_id': user_id,
                'type': data['type'],
                'balance': balance,
                'interest_rate': interest_rate
            }
            
            # Create account
            try:
                account = self.account_dao.create_account(account_data)
                if not account:
                    raise ValueError("Failed to create account")
                logger.info(f"Created account {account.account_number} for user {user_id}")
            except ValueError as e:
                # If account creation fails, we should still propagate the error
                raise e
            
            # Create initial deposit transaction if balance > 0
            if balance > 0:
                try:
                    transaction_data = {
                        'account_id': account.account_number,
                        'type': 'DEPOSIT',
                        'amount': balance,
                        'description': 'Initial deposit'
                    }
                    
                    transaction_id = self.transaction_dao.create_transaction(transaction_data)
                    if not transaction_id:
                        raise ValueError("Failed to create initial deposit transaction")
                    logger.info(f"Created initial deposit transaction: {transaction_id}")
                except Exception as e:
                    logger.error(f"Error creating initial deposit: {e}")
                    # We don't raise here as the account is already created
            
            return account
                
        except ValueError as e:
            logger.error(f"Validation error in create_account: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_account: {str(e)}")
            raise ValueError(f"Account creation failed: {str(e)}")

    def delete_account(self, account_number: int) -> None:
        """Delete an account"""
        try:
            logger.info(f"Deleting account {account_number}")
            if not self._check_edit_permission(account_number):
                raise Forbidden("You don't have permission to delete this account")
            
            account = self.account_dao.get_account_by_number(account_number)
            if not account:
                raise NotFound(f"Account {account_number} not found")

            if account.balance > 0:
                raise ValueError("Cannot delete account with positive balance")

            self.account_dao.delete_account(account_number)
            logger.info(f"Successfully deleted account {account_number}")
        except Exception as e:
            logger.error(f"Error deleting account {account_number}: {str(e)}")
            raise

    def get_account_transactions(self, account_number: int) -> List[Dict]:
        """Get all transactions for an account"""
        try:
            logger.info(f"Fetching transactions for account {account_number}")
            if not self.account_dao.get_account_by_number(account_number):
                raise NotFound(f"Account {account_number} not found")
                
            transactions = self.account_dao.get_account_transactions(account_number)
            logger.info(f"Found {len(transactions)} transactions")
            return transactions
        except Exception as e:
            logger.error(f"Error fetching transactions: {str(e)}")
            raise

    def _check_edit_permission(self, account_number: int) -> bool:
        """Check if current admin has permission to edit account"""
        admin_id = session.get('admin_id')
        try:
            # TODO: Implement actual permission checking logic
            return True
        except Exception as e:
            logger.error(f"Error checking permissions for admin {admin_id} on account {account_number}: {str(e)}")
            raise

    def search_accounts(self, search_term: str) -> List[Account]:
        """Search accounts by name or account number"""
        try:
            if not search_term:
                logger.warning("Empty search term provided")
                raise ValueError("Search term cannot be empty")
                
            logger.info(f"Searching accounts with term: {search_term}")
            accounts = self.account_dao.search_accounts(search_term)
            
            logger.info(f"Found {len(accounts)} matching accounts")
            return accounts
            
        except Exception as e:
            logger.error(f"Error searching accounts: {str(e)}")
            raise
    def process_deposit(self, account_number: int, amount: float, description: str = None) -> bool:
        """Process a deposit transaction"""
        try:
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            amount_decimal = Decimal(str(amount))
            logger.info(f"Processing deposit: Account={account_number}, Amount={amount_decimal}")
            
            return self.transactiondao.deposit(account_number, amount_decimal, description)
            
        except Exception as e:
            logger.error(f"Error processing deposit: {str(e)}")
            raise

    def process_withdrawal(self, account_number: int, amount: float, description: str = None) -> bool:
        """Process a withdrawal transaction"""
        try:
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            amount_decimal = Decimal(str(amount))
            logger.info(f"Processing withdrawal: Account={account_number}, Amount={amount_decimal}")
            
            return self.transaction_dao.withdraw(account_number, amount_decimal, description)
            
        except Exception as e:
            logger.error(f"Error processing withdrawal: {str(e)}")
            raise

    def process_transfer(self, from_account: int, to_account: int, amount: float, description: str = None) -> bool:
        """Process a transfer between accounts"""
        try:
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            if from_account == to_account:
                raise ValueError("Cannot transfer to same account")
                
            amount_decimal = Decimal(str(amount))
            logger.info(f"Processing transfer: From={from_account}, To={to_account}, Amount={amount_decimal}")
            
            return self.transaction_dao.transfer(from_account, to_account, amount_decimal, description)
            
        except Exception as e:
            logger.error(f"Error processing transfer: {str(e)}")
            raise

    def get_bank_statement(self, account_number: int, start_date: str = None, end_date: str = None) -> Dict:
        """Get bank statement for an account"""
        try:
            logger.info(f"Generating bank statement for account {account_number}")
            
            # Convert date strings to datetime objects if provided
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            
            statement = self.account_dao.get_bank_statement(account_number, start_date_obj, end_date_obj)
            
            logger.info(f"Generated statement with {len(statement['transactions'])} transactions")
            return statement
            
        except ValueError as e:
            logger.error(f"Invalid date format: {str(e)}")
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        except Exception as e:
            logger.error(f"Error generating bank statement: {str(e)}")
            raise