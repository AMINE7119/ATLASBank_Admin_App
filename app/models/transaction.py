 
# app/models/transaction.py
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class Transaction:
    id: int
    account_number: int
    operation_type: str
    amount: Decimal
    recipient_account: int = None
    transaction_date: datetime = None
    description: str = None
