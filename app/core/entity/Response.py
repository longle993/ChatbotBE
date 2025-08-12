from typing import Any, Optional
from pydantic import BaseModel

class ApiResponse(BaseModel):
    code: int
    isSuccess: bool
    message: str
    data: Optional[Any] = None

    @staticmethod
    def success(data: Any = None, message: str = "Success", code: int = 200):
        return ApiResponse(
            code=code,
            isSuccess=True,
            message=message,
            data=data
        )

    @staticmethod
    def error(message: str = "Error", code: int = 500, data: Any = None):
        return ApiResponse(
            code=code,
            isSuccess=False,
            message=message,
            data=data
        )
