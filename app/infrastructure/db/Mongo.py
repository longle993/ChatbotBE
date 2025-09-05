from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from config import Config
import os
from dotenv import load_dotenv
load_dotenv()
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://fastchatbot:i87M6dFZdLrRaDUn@cluster0.eetjn7s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
DB_NAME = os.getenv("DB_NAME", "Chatbot")

client: AsyncIOMotorClient | None = None

async def get_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(MONGO_URI)
    return client

async def get_user_collection() -> Collection:
    cli = await get_client()
    return cli[DB_NAME]["users"]

async def get_conversation_collection() -> Collection:
    cli = await get_client()
    return cli[DB_NAME]["conversations"]
