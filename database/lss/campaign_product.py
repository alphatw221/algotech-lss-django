from ._config import db
from ._config import Collection
from datetime import datetime
from api import models
__collection = db.api_campaign_product


class CampaignProduct(Collection):

    _collection = db.api_campaign_product
    collection_name='api_campaign_product'
    template = models.campaign.campaign_product.api_campaign_product_template
    
    def sold_from_external(self, qty, sync=True, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'qty_sold': qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)
            
    def set_qty_sold(self, qty, sync=True, session=None):
        self._collection.update_one({'id':self.id},{"$set":{'qty_sold':qty, 'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)

    def sold(self, qty, sync=True, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'qty_sold': qty, 'qty_add_to_cart': -qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)

    def add_to_cart(self, qty, sync=True, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'qty_add_to_cart': qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)

    def customer_return(self, qty, sync=True, session=None):

        self._collection.update_one({'id':self.id}, {"$inc": {'qty_add_to_cart': -qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)