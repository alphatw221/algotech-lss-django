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
    

    def clear(self, session=None):
        self.update(session=session, sync=False, seller_adjust=[], free_delivery = False, products={}, meta={})

    def remove_product(self, campaign_product_id, sync=False, session=None):
        self._collection.update_one({"id":self.id},{"$unset":{f"products.{campaign_product_id}":1}})
        if sync:
            self._sync()