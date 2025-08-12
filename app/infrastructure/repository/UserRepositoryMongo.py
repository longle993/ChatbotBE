from core.entity.User import User
from core.interface.IUserRepository import IUserRepository
from bson import ObjectId
from pymongo.collection import Collection
from utils.hashSHA256 import hash_password 

class UserRepositoryMongo(IUserRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    async def create(self, user: User) -> User:
        doc = {
            "username": user.username,
            "email": user.email,
            "password": user.password,
            "full_name": user.full_name,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        result = await self.collection.insert_one(doc)
        user.id = str(result.inserted_id)
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not doc:
            return None
        return User(
            id=str(doc["_id"]),
            username=doc["username"],
            email=doc["email"],
            created_at=doc["created_at"]
        )
    
    async def login(self, username: str, password: str) -> User | None:
        doc = await self.collection.find_one({"username": username, "password": hash_password(password)})
        if not doc:
            return None
        return User(
            id=str(doc["_id"]),
            username=doc["username"],
            email=doc["email"]
        )
