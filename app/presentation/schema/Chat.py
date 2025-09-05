from pydantic import BaseModel
from core.entity.Response import ApiResponse
from typing import Any, Optional, List
from fastapi import UploadFile


#Chat
class CreateChatRequest(BaseModel):
    conversation_id: str
    message: str
    files: Optional[List[UploadFile]] = None
    
    class Config:
        arbitrary_types_allowed = True

class CreateChatResponse(BaseModel):
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
                "reply": response.data.message
            }
        )
