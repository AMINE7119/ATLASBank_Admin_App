from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    date_of_birth: datetime
    status: bool
    gender: str
    job: str
    created_at: datetime = None

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"