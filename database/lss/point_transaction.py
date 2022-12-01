from ._config import db
from ._config import Collection
from api import models

__collection = db.api_point_transaction


class BuyerPoint(Collection):

    _collection = db.api_point_transaction
    collection_name='api_point_transaction'
    template = models.user.point_transaction.api_point_transaction_template
    
    

