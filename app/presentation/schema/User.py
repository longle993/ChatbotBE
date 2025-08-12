from pydantic import BaseModel, EmailStr
from core.entity.Response import ApiResponse
from typing import Any, Optional

#Create
class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str

class CreateUserResponse(BaseModel):
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
                "user": response.data.username,
                "email": response.data.email
            }
        )

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
                "user": response.data.username,
                "email": response.data.email
            }
        )
