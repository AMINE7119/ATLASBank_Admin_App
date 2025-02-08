# app/services/bank_service.py
from typing import List, Optional, Dict, Any
from flask import session
from werkzeug.exceptions import NotFound, Forbidden, Unauthorized
from app.models.account import Account
from app.dal.account_dao import AccountDAO
from app.logger.app_logging import setup_logging
from functools import wraps

logger = setup_logging()

class BankService:
    def __init__(self):
        self.account_dao = AccountDAO()

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

            updated_account = self.account_dao.update_account(account_number, data)
            logger.info(f"Successfully updated account {account_number}")
            return updated_account
        except Exception as e:
            logger.error(f"Error updating account {account_number}: {str(e)}")
            raise

    def create_account(self, data: Dict[str, Any]) -> Account:
        """Create new account"""
        try:
            logger.info("Creating new account")
            account = self.account_dao.create_account(data)
            logger.info(f"Successfully created account {account.account_number}")
            return account
        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            raise

    def delete_account(self, account_number: int) -> None:
        """Delete an account"""
        try:
            logger.info(f"Deleting account {account_number}")
            if not self._check_edit_permission(account_number):
                raise Forbidden("You don't have permission to delete this account")
            
            if not self.account_dao.get_account_by_number(account_number):
                raise NotFound(f"Account {account_number} not found")

            self.account_dao.delete_account(account_number)
            logger.info(f"Successfully deleted account {account_number}")
        except Exception as e:
            logger.error(f"Error deleting account {account_number}: {str(e)}")
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