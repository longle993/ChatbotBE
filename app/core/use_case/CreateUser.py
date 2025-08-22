from datetime import datetime
from core.entity.User import User
from core.interface.IUserRepository import IUserRepository

class CreateUser:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def execute(self, username: str, password: str, full_name: str, email: str) -> User:
        user = User(
        username=username,
        password=password,
        full_name=full_name,
        email=email,
        created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return await self.user_repo.create(user)

