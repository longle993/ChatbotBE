from pydantic import BaseModel, EmailStr
from core.entity.Response import ApiResponse
from typing import Any, Optional
from core.entity.Chat import Message

#Create
class CreateConversationRequest(BaseModel):
    user_id: str
    title: str
    messages: Optional[list[Message]] = []

class CreateConversationResponse(BaseModel):
    code: int
    isSuccess: bool
    message: str
    data: Optional[Any] = None

    @classmethod
    def from_entity(cls, response: ApiResponse):
        return cls(
            code=response.code,
            isSuccess=response.isSuccess,
            message=response.message,
            data={
                "user_id": response.data.user_id,
                "title": response.data.title,
                "created_at": response.data.created_at,
                "updated_at": response.data.updated_at,
                "is_active": response.data.is_active
            }
        )

class CreateConversationResponse(BaseModel):
    code: int
    isSuccess: bool
    message: str
    data: Optional[Any] = None

    @classmethod
    def from_entity(cls, response: ApiResponse):
        return cls(
            code=response.code,
            isSuccess=response.isSuccess,
            message=response.message,
            data={
                "conversation": response.data
            }
        )

#Get Conversations
class GetConversationRequest(BaseModel):
    Conversation_id: str

class GetConversationResponse(BaseModel):
    code: int
    isSuccess: bool
    message: str
    data: Optional[Any] = None

    @classmethod
    def from_entity(cls, response: ApiResponse):
        return cls(
            code=response.code,
            isSuccess=response.isSuccess,
            message=response.message,
            data={
                "conversations": response.data
            }
        )
