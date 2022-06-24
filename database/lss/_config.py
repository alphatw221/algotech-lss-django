from pymongo import MongoClient
from django.conf import settings


client = MongoClient(settings.MONGODB_CONNECTION_STRING)
db = client[settings.MONGODB_DATABASE_NAME]


class Collection():

    _collection=None

    @classmethod
    def get(cls , **kwargs):
        return cls._collection.find_one(kwargs)
    
    @classmethod
    def filter(cls , **kwargs):
        return cls._collection.find(kwargs)