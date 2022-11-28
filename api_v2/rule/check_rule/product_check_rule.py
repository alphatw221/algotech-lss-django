import lib
from api import models
class ProductCheckRule():

    @staticmethod
    def is_max_order_amount_less_than_qty(**kwargs):
        product_data = kwargs.get('product_data')
        max_order_amount = product_data.get('max_order_amount')
        if not max_order_amount:
            return
        if max_order_amount > product_data.get('qty',0):
            raise lib.error_handle.error.api_error.ApiVerifyError('helper.max_order_amount_should_less_than_stock')

    @staticmethod
    def is_images_type_supported(**kwargs):
        image = kwargs.get('image')
        
        if image in ['null', None, '', 'undefined', '._no_image']:
            return 
        elif image.content_type not in models.product.product.IMAGE_SUPPORTED_TYPE:
            print(image.content_type)
            raise lib.error_handle.error.api_error.ApiVerifyError('helper.not_support_this_image_type')
    
    @staticmethod 
    def is_images_exceed_max_size(**kwargs):
        image = kwargs.get('image')
        
        if image in ['null', None, '', 'undefined', '._no_image']:
            return 
        if image.size > models.product.product.IMAGE_MAXIMUM_SIZE:
            print(image.size)
            raise lib.error_handle.error.api_error.ApiVerifyError('helper.image_size_exceed_maximum_size')
  