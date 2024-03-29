from ._config import db
from ._config import Collection
from datetime import datetime
from api import models
__collection = db.api_order_product


class OrderProduct(Collection):

    _collection = db.api_order_product
    collection_name='api_order_product'
    template = models.order.order_product.api_order_product_template
    @classmethod
    def transfer_to_order(cls, pre_order=None, order=None, session=None):
        cls._collection.update_many(
                    {"pre_order_id": pre_order.id},
                    {
                        "$set": {"pre_order_id": None, "order_id": order.id, "updated_at":datetime.utcnow()}
                    }, 
                    session=session)