from pymongo import MongoClient
from django.conf import settings


client = MongoClient(settings.MONGODB_CONNECTION_STRING)
db = client[settings.MONGODB_DATABASE_NAME]


def get_incremented_filed(collection_name, field_name, session=None):
    assert field_name=='id'

    if session:
        doc = db['__schema__'].find_one({"name":collection_name}, session=session)
        db['__schema__'].update_one({"name":collection_name},{"$inc":{"auto.seq":1}}, session=session)
            
        return int(doc['auto']['seq']+1)

    with client.start_session() as session:
        with session.start_transaction():
            
            doc = db['__schema__'].find_one({"name":collection_name}, session=session)
            db['__schema__'].update_one({"name":collection_name},{"$inc":{"auto.seq":1}}, session=session)
            
    return int(doc['auto']['seq']+1)
