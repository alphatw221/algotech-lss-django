from ._config import db
from ._config import Collection
from api import models
from datetime import datetime

__collection = db.api_pre_order

def get_oid_by_id(id):
    return str(__collection.find_one({"id":id})['_id'])

class PreOrder(Collection):

    _collection = db.api_pre_order
    collection_name='api_pre_order'
    template = models.order.pre_order.api_pre_order_template
    
    def delete_product(self, campaign_product, sync=True, session=None, **kwargs):
        db.api_pre_order.update_one(
            {'id': self.id},
            {
                "$unset":{
                    f"products.{str(campaign_product.id)}": "",
                },
                "$set": {
                    'updated_at':datetime.utcnow(),
                    **kwargs
                },
            },session=session)
        if sync:
            self._sync(session=session)

    def reset_pre_order(self, sync=True):

        db.api_pre_order.update_one(
            {'id': self.id},
            {
                "$set": {
                    "products":{},
                    "total" : 0,
                    "subtotal" : 0,
                    "discount" : 0,
                    "adjust_price":0, 
                    "adjust_title":"", 
                    "free_delivery":False, 
                    "history":{}, 
                    "meta":{},
                    "applied_discount":{},

                    'updated_at':datetime.utcnow()
                },
            }
        )
        if sync:
            self._sync()

