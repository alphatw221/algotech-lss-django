from ._config import db
from ._config import Collection
from datetime import datetime

__collection = db.api_product


class Product(Collection):

    _collection = db.api_product
    collection_name='api_product'
    
    def distribute(self, qty, sync=True, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'qty': -qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)

    def restock(self, qty, sync=True, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'qty': qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)
