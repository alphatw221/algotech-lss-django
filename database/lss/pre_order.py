from ._config import db
from ._config import Collection
from api import models

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
                "$set": kwargs,
            },session=session)
        if sync:
            self.__sync(session=session)