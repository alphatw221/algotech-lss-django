from django.conf import settings

from .default import DefaultCampaignProductImportProcessor, ProductCategoriesFieldMapper
from lib.helper.import_helper import FieldMapper
from api import models

CONTENT_TYPE_XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
CONTENT_TYPE_CSV = 'text/csv'
class SHCProductImportProcessor(DefaultCampaignProductImportProcessor):
    
    
    def __init__(self, user_subscription, campaign, size_limit_bytes=100*1024, accept_types=[CONTENT_TYPE_XLSX, CONTENT_TYPE_CSV]) -> None:

        self.user_subscription = user_subscription
        self.campaign = campaign
        product_category_dict = {product_category.name:product_category.id for product_category in user_subscription.product_categories.all()}
        self.sheet_name = 'sheets'
        self.size_limit_bytes = size_limit_bytes
        self.accept_types = accept_types

        self.field_mappers = [
            FieldMapper('SKU', 'sku', ''),
            FieldMapper('Description', 'name', ''),
            FieldMapper('Description', 'description', ''),
            FieldMapper('Keyword', 'order_code', ''),
            FieldMapper('Price', 'price', 0),
            FieldMapper('Stock', 'qty_for_sale', 0),
            FieldMapper('MaxQty', 'max_order_amount', 0),
            ProductCategoriesFieldMapper('Supplier', 'categories', [], product_category_dict=product_category_dict, user_subscription = user_subscription),
            FieldMapper('Photo URL', 'image', settings.GOOGLE_STORAGE_STATIC_DIR+models.product.product.IMAGE_NULL),

        ]