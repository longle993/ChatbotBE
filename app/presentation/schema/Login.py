from pydantic import BaseModel
from core.entity.Response import ApiResponse
from typing import Any, Optional

#Login
class LoginUserRequest(BaseModel):
    username: str
    password: str

class LoginUserResponse(BaseModel):
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
                "exp": response.data.exp
            }
        )