from dataclasses import dataclass
from datetime import datetime

@dataclass
class Admin:
    id: int
    username: str
    password: str
    email: str
    role: str
    is_active: bool
    last_login: datetime = None
    created_at: datetime = None