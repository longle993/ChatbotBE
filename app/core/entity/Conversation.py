from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from core.entity.Chat import Message

class Conversation(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

    class Config:
        from_attributes = True