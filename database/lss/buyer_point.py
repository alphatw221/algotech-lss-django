from ._config import db
from ._config import Collection
from api import models

__collection = db.api_user_point


class BuyerPoint(Collection):

    _collection = db.api_user_point
    collection_name='api_user_point'
    template = models.user.buyer_point.api_user_point_template
    
    

