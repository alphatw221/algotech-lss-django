from ._config import db
from ._config import Collection
from api import models

__collection = db.api_user_register

def get_oid_by_id(id):
    return str(__collection.find_one({"id":id})['_id'])

class UserRegister(Collection):

    _collection = db.api_user_register
    collection_name='api_user_register'
    
