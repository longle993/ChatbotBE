from pydantic import BaseModel
from core.entity.Response import ApiResponse
from typing import Any, Optional

class AuthResponse(BaseModel):
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
                "data": response.data
            }
        )




