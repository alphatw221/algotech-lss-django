from ._config import db
from ._config import Collection

__collection = db.api_pre_order

def get_oid_by_id(id):
    return str(__collection.find_one({"id":id})['_id'])

class PreOrder(Collection):

    _collection = db.api_pre_order