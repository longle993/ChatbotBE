from core.entity.User import User
from core.interface.IUserRepository import IUserRepository
from bson import ObjectId
from pymongo.collection import Collection
from utils.hashArgon2 import HashArgon2, VerifyArgon2
from fastapi import HTTPException, status

class UserRepositoryMongo(IUserRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    async def create(self, user: User) -> User:
        doc = {
            "username": user.username,
            "email": user.email,
            "password": HashArgon2(user.password),
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
        doc = await self.collection.find_one({"username": username})
        if not doc:
            return None

        if not VerifyArgon2(doc["password"], password):
            print("Password verification failed")
            return None
       
        return User(
            id=str(doc["_id"]),
            username=doc["username"],
            email=doc["email"],
            role=doc["role"]
        )

    async def get_users(self, role: str, id: str, username: str) -> list[User]:
        doc = await self.collection.find_one({"username": username, "_id": ObjectId(id)})
        userRole = ''
        if doc:
            userRole = str(doc.get("role", ""))
        
        
        if userRole != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        query = {}
        docs = await self.collection.find(query).to_list(length=None)
        return [
            User(
                id=str(doc["_id"]),
                username=doc["username"],
                full_name=doc["full_name"],
                email=doc["email"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                role=doc["role"],
            )
            for doc in docs
        ]

