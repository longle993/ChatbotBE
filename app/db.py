from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from .config import Config

mongo = None  # Biến toàn cục để lưu client

def init_db():
    global mongo
    mongo = MongoClient(Config.MONGO_URI, server_api=ServerApi('1'))
    try:
        mongo.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)