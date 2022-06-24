from ._config import db
from ._config import client

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
