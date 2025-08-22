from core.entity.User import User
from core.interface.IUserRepository import IUserRepository

class GetUser:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def execute(self, role:str, id: str, username: str) -> list[User]:
        return await self.user_repo.get_users(role, id, username)