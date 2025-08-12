from pydantic import BaseModel, EmailStr
from core.entity.Response import ApiResponse
from typing import Any, Optional

#Chat
class CreateChatRequest(BaseModel):
    message: str

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

