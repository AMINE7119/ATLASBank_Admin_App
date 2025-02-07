 
# app/models/user.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    username: str
    email: str
    phone_number: str
    job: str
    created_at: datetime = None