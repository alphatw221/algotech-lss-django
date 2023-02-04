from .default import DefaultProductImportProcessor, ProductCategoriesFieldMapper, CONTENT_TYPE_CSV, CONTENT_TYPE_XLSX

from lib.helper.import_helper import FieldMapper
class SHCProductImportProcessor(DefaultProductImportProcessor):
    

    def __init__(self, user_subscription, size_limit_bytes=1024*1024*10, accept_types=[CONTENT_TYPE_XLSX, CONTENT_TYPE_CSV]) -> None:

        self.user_subscription = user_subscription
        product_category_dict = {product_category.name:product_category.id for product_category in user_subscription.product_categories.all()}
        self.sheet_name = 'sheets'
        self.size_limit_bytes = size_limit_bytes
        self.accept_types = accept_types

        self.field_mappers = [
            FieldMapper('Description', 'name', ''),
            FieldMapper('SKU', 'sku', ''),
            FieldMapper('Description', 'description', ''),
            FieldMapper('Keyword', 'order_code', ''),
            FieldMapper('Price', 'price', 0),
            FieldMapper('Stock', 'qty', 0),
            FieldMapper('MaxQty', 'max_order_amount', 0),
            ProductCategoriesFieldMapper('Supplier', 'categories', [], product_category_dict=product_category_dict, user_subscription = user_subscription)
        ]