from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class Message(BaseModel):
    id: Optional[str] = None
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
