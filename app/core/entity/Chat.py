from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class Message(BaseModel):
    id: Optional[str] = None
    role: str  # "user" hoặc "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
