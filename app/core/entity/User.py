from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: str | None = None
    username: str | None = None
    password: str | None = None
    full_name: str | None = None
    email: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
