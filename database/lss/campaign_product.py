from ._config import db
from ._config import Collection
from datetime import datetime

__collection = db.api_campaign_product


class CampaignProduct(Collection):

    _collection = db.api_campaign_product
    collection_name='api_campaign_product'
    
    def sold(self, qty, sync=True, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'qty_sold': qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)

    def customer_return(self, qty, sync=True, session=None):

        self._collection.update_one({'id':self.id}, {"$inc": {'qty_sold': -qty,"$set":{'updated_at':datetime.utcnow()}}}, session=session)
        if sync:
            self._sync(session=session)