from ._config import db
from ._config import Collection
from datetime import datetime
from api import models

__collection = db.api_product_category


class ProductCategory(Collection):

    _collection = db.api_product_category
    collection_name='api_product_category'
    template = models.product.product_category.api_product_category_template
    