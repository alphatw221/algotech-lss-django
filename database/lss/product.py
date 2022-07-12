from ._config import db
from ._config import Collection
from datetime import datetime

__collection = db.api_product


class Product(Collection):

    _collection = db.api_product
    collection_name='api_product'
    
  