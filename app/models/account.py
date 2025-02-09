# app/models/account.py
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass
class Account:
    account_number: int
    user_id: int
    account_type: str
    balance: Decimal
    is_active: bool = True
    interest_rate: Decimal = Decimal('0.00')
    created_at: Optional[datetime] = None
    holder_name: Optional[str] = None
    holder_email: Optional[str] = None
