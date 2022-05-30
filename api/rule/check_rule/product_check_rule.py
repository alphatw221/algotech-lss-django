import lib

class ProductCheckRule():

    @staticmethod
    def is_max_order_amount_less_than_qty(**kwargs):
        product_data = kwargs.get('product_data')
        max_order_amount = product_data.get('max_order_amount')
        if not max_order_amount:
            return
        if max_order_amount > product_data.get('qty',0):
            raise lib.error_handle.error.api_error.ApiVerifyError('max order amount should be less than stock amount')

  