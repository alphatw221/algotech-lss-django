from pendulum import datetime
from pymongo import MongoClient
from django.conf import settings

from datetime import datetime

client = MongoClient(settings.MONGODB_CONNECTION_STRING)
db = client[settings.MONGODB_DATABASE_NAME]


class Collection():

    _collection=None
    collection_name=''

    def __init__(self, id, _id, data):
        self.id = id
        self._id = _id
        self.data = data

    
    @classmethod
    def get(cls , projecter = None, session=None, **kwargs):
        return cls._collection.find_one(kwargs, projecter, session=session)
    
    @classmethod
    def filter(cls ,projecter = None, session=None, **kwargs):
        return cls._collection.find(kwargs, projecter, session=session)

    @classmethod
    def get_object(cls, session=None, **kwargs):
        data = cls.get(**kwargs)
        if not data:
            return None
        return cls(data.get('id'), data.get('_id'), data)

    @classmethod
    def create(cls, session=None, **kwargs):

        kwargs['id'] = cls.__get_incremented_filed(session=session)
        kwargs['created_at'] = datetime.utcnow()
        _id = cls._collection.insert_one(kwargs, session=session).inserted_id
        data = cls._collection.find_one(_id, session=session)
        return cls(data.get('id'), data.get('_id'), data)

    
    @classmethod
    def __get_incremented_filed(cls, session=None):
        if session:
            doc = db['__schema__'].find_one({"name":cls.collection_name}, session=session)
            db['__schema__'].update_one({"name":cls.collection_name},{"$inc":{"auto.seq":1}}, session=session)
                
            return int(doc['auto']['seq']+1)

        with client.start_session() as session:
            with session.start_transaction():
                
                doc = db['__schema__'].find_one({"name":cls.collection_name}, session=session)
                db['__schema__'].update_one({"name":cls.collection_name},{"$inc":{"auto.seq":1}}, session=session)
                
        return int(doc['auto']['seq']+1)

    def _sync(self, session=None):
        self.data = self._collection.find_one({'id':self.id}, session=session)


    def update(self, session=None, sync = True, **kwargs):
        kwargs['updated_at'] = datetime.utcnow()
        self._collection.update_one({'id': self.id},{"$set": kwargs},session=session)
        if sync:
            self._sync(session = session)
    
    def delete(self, session=None):
        self._collection.delete_one({'id': self.id}, session=session)