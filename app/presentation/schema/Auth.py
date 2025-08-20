from pydantic import BaseModel
from typing import Any, Optional

class AuthResponse(BaseModel):
    code: int
    isSuccess: bool
    message: str
    data: Optional[Any] = None
 
    @classmethod
    def success(cls, message: str, data: Any = None):
        return cls(
            code=200,
            isSuccess=True,
            message=message,
            data=data
        )

    @classmethod
    def error(cls, code: int, message: str):
        return cls(
            code=code,
            isSuccess=False,
            message=message,
            data=None
        )
