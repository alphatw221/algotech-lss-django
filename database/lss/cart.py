from ._config import db
from ._config import Collection
from api import models

__collection = db.api_cart

def get_oid_by_id(id):
    return str(__collection.find_one({"id":id})['_id'])

class Cart(Collection):

    _collection = db.api_cart
    collection_name='api_cart'
    template = models.cart.cart.api_cart_template
    
    def clear(self, sync=False, session=None):
        self.update(session=session, sync=sync, adjust_title=None, adjust_price=0, free_delivery = False, products={}, applied_discount={}, discount=0)

    def remove_product(self, campaign_product_id, sync=False, session=None):
        self._collection.update_one({"id":self.id},{"$unset":{f"products.{campaign_product_id}":1}})
        if sync:
            self._sync()

def get_count_in_campaign(campaign_id):
    if campaign_id:
        return __collection.find({'campaign_id': campaign_id, 'products': {'$ne': {}}}).count()
    return 0
