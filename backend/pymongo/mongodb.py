from pymongo import MongoClient
from django.conf import settings

# from automation.management.commands.auto import DBException
# from lss import settings_rq as settings

client = MongoClient(settings.MONGODB_CONNECTION_STRING)
db = client[settings.MONGODB_DATABASE_NAME]


def get_incremented_filed(collection_name, field_name):
    try:
        with client.start_session() as session:
            with session.start_transaction():
                doc=db.auto_increment.find_one({"collection_name":collection_name, "field_name":field_name}, session=session)
                increased_number=doc['number']+1
                db.auto_increment.update_one({"collection_name":collection_name, "field_name":field_name},{"$set":{"number":increased_number}}, session=session)
    except Exception as e:
        raise DBException
    return increased_number