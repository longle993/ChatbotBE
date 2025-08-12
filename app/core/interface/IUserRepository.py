from abc import ABC, abstractmethod
from core.entity.User import User

class IUserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None:
        pass

    @abstractmethod
    async def login(self, username: str, password:str) -> User | None:
        pass
