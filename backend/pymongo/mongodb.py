from pymongo import MongoClient
from django.conf import settings

from pymongo import errors as pymongo_error
# from lss import settings_rq as settings

client = MongoClient(settings.MONGODB_CONNECTION_STRING)
db = client[settings.MONGODB_DATABASE_NAME]


def get_incremented_filed(collection_name, field_name):
    with client.start_session() as session:
        with session.start_transaction():
            # doc=db.auto_increment.find_one({"collection_name":collection_name, "field_name":field_name}, session=session)
            # increased_number=doc['number']+1
            # db.auto_increment.update_one({"collection_name":collection_name, "field_name":field_name},{"$set":{"number":increased_number}}, session=session)

            assert field_name=='id'

            doc = db['__schema__'].find_one({"name":collection_name}, session=session)
            db['__schema__'].update_one({"name":collection_name},{"$inc":{"auto.seq":1}}, session=session)
            
    return int(doc['auto']['seq']+1)

    # try:
    #     with client.start_session() as session:
    #         with session.start_transaction():
    #             doc=db.auto_increment.find_one({"collection_name":collection_name, "field_name":field_name}, session=session)
    #             increased_number=doc['number']+1
    #             db.auto_increment.update_one({"collection_name":collection_name, "field_name":field_name},{"$set":{"number":increased_number}}, session=session)
    #     return increased_number
    # except Exception as e:
    #     print(e)
    #     return 0
    #     # raise pymongo_error.E