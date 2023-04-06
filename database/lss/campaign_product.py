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

    # def sold(self, qty, sync=True, session=None):
    #     self._collection.update_one({'id':self.id},{"$inc": {'qty_sold': qty, 'qty_add_to_cart': -qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
    #     if sync:
    #         self._sync(session=session)

    def add_to_cart(self, qty, sync=True, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'qty_add_to_cart': qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)

    def customer_return(self, qty, sync=True, session=None):

        self._collection.update_one({'id':self.id}, {"$inc": {'qty_add_to_cart': -qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)

    def checkout(self, qty, sync=True, session=None):

        self._collection.update_one({'id':self.id},{"$inc": {'qty_pending_payment': qty, 'qty_add_to_cart': -qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)
    
    def sold(self, qty, sync=True, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'qty_sold': qty, 'qty_pending_payment': -qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)

    def return_after_checkout(self, qty, sync=True, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'qty_pending_payment': -qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)


    def return_after_paid(self, qty, sync=True, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'qty_sold': -qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)


    def back_to_cart(self, qty, sync=True, session=None):
        self._collection.update_one({'id':self.id},{"$inc": {'qty_pending_payment': -qty, 'qty_add_to_cart': qty},"$set":{'updated_at':datetime.utcnow()}}, session=session)
        if sync:
            self._sync(session=session)


# def remove_categories(product_category_id, session=None):
#     __collection.update_many({f"categories.{str(product_category_id)}":{"$exists":True}},{"$unset":{f"categories.{str(product_category_id)}":1}}, session=session)



# def remove_categories(user_subscription_id, product_category_id, session=None):
#     __collection.update_one(
#         {
#             "user_subscription_id":user_subscription_id,
#             "categories":str(product_category_id)
#         },
#         {"$pull":{"categories":str(product_category_id)}}, 
#         session=session)

def remove_categories(product_category_id, session=None):
    __collection.update_many(
        {
            "categories":str(product_category_id)
        },
        {"$pull":{"categories":str(product_category_id)}}, 
        session=session)