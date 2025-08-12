from core.entity.User import User
from core.interface.IUserRepository import IUserRepository

class LoginUser:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def execute(self, username: str, password: str) -> User | None:
        return await self.user_repo.login(username, password)