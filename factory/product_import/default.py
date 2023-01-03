import lib
import pandas
from api import models
from lib.helper.import_helper import FieldMapper
import io
import json

CONTENT_TYPE_XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
CONTENT_TYPE_CSV = 'text/csv'

class ProductCategoriesFieldMapper(FieldMapper):
    
    def get_model_data(self, object):
        try:
            product_category_dict = self.kwargs.get('product_category_dict')
            user_subscription = self.kwargs.get('user_subscription')

            product_category_name = super().get_model_data(object)
            if not product_category_name:
                return []
            if product_category_name in product_category_dict:
                return [str(product_category_dict.get(product_category_name))]
            else:
                product_category = models.product.product_category.ProductCategory.objects.create(
                    user_subscription = user_subscription, 
                    name = product_category_name)
                product_category_dict[product_category_name] = product_category.id
                return [str(product_category.id)]
        except Exception:
            import traceback
            print(traceback.format_exc())
            return []


class DefaultProductImportProcessor(lib.helper.import_helper.ImportProcessor):

    def __init__(self, user_subscription, size_limit_bytes=1024*1024*10, accept_types=[CONTENT_TYPE_XLSX, CONTENT_TYPE_CSV]) -> None:

        self.user_subscription = user_subscription
        product_category_dict = {product_category.name:product_category.id for product_category in user_subscription.product_categories.all()}
        self.sheet_name = 'sheets'
        
        super().__init__(size_limit_bytes, accept_types)
        self.field_mappers = [
            FieldMapper('Product Name', 'name', ''),
            FieldMapper('SKU', 'sku', ''),
            FieldMapper('Description', 'description', ''),
            FieldMapper('Keyword', 'order_code', ''),
            FieldMapper('Cost', 'price_ori', ''),
            FieldMapper('Price', 'price', ''),
            FieldMapper('Stock', 'qty', ''),
            FieldMapper('MaxQty', 'max_order_amount', ''),
            # FieldMapper('Reply Message', 'sku', ''),
            ProductCategoriesFieldMapper('Supplier', 'categories', [], product_category_dict=product_category_dict, user_subscription = user_subscription)
        ]

    def size_not_valid(self):
        raise lib.error_handle.error.api_error.ApiVerifyError('size_invalid')


    def type_not_valid(self):
        raise lib.error_handle.error.api_error.ApiVerifyError('type_invalid')


    def file_to_data(self, file):

        if file.content_type == CONTENT_TYPE_XLSX:
            excel_data_df = pandas.read_excel(io.BytesIO(file.read()), sheet_name=self.sheet_name)
            return json.loads( excel_data_df.to_json(orient='records'))
        elif file.content_type == CONTENT_TYPE_CSV:
            excel_data_df = pandas.read_csv(io.BytesIO(file.read()))
            return json.loads( excel_data_df.to_json(orient='records'))

    def save_data(self, data):
        
        for object in data:
            try:
                data = {
                    'user_subscription':self.user_subscription,
                    **{field_mapper.model_field:field_mapper.get_model_data(object) for field_mapper in self.field_mappers}
                }
                models.product.product.Product.objects.create(**data)
            except Exception:
                import traceback
                print(traceback.format_exc())
