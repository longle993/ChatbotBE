import os


class Config:
    MONGO_URI = os.environ.get('MONGO_URI')
