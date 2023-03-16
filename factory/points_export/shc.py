from .default import DefaultPointsExportProcessor

from api import models



from lib.helper.xlsx_helper import FieldMapper

from datetime import datetime

class DateTimeMapper(FieldMapper):
    def get_field_data(self, object):

        return super().get_field_data(object).strftime("%Y-%m-%d") if type(super().get_field_data(object)) == datetime else None


class ShippingNameMapper(FieldMapper):
    def get_field_data(self, object):
        return f"{str(object.get('shipping_last_name'))} {str(object.get('shipping_first_name'))}"


class ShippingMethodMapper(FieldMapper):
    def get_field_data(self, object):
        #TODO i18n
        return 'Delivery' if super().get_field_data(object)== models.order.order.SHIPPING_METHOD_DELIVERY else 'Pick Up'

class ShippingOptionMapper(FieldMapper):
    def get_field_data(self, object):
        
        shipping_option=super().get_field_data(object)
        shipping_option = 'Default' if shipping_option == '' else shipping_option
        return shipping_option

class DeliveryInfonMapper(FieldMapper):
    def get_field_data(self, object):
        return '' if object.get('shipping_method') == models.order.order.SHIPPING_METHOD_PICKUP else super().get_field_data(object)


class PickupStoreMapper(FieldMapper):
    def get_field_data(self, object):
        if object.get('shipping_method') != models.order.order.SHIPPING_METHOD_PICKUP:
            return ''
        return object.get('shipping_option_data',{}).get('name') if object.get('shipping_option_data',{}).get('name') else 'Default'
        
class PickupAddressMapper(FieldMapper):
    def get_field_data(self, object):
        if object.get('shipping_method') != models.order.order.SHIPPING_METHOD_PICKUP:
            return ''
        return object.get('shipping_option_data',{}).get('name') if object.get('shipping_option_data',{}).get('address') else 'Default'
        
class PaymentMethodMapper(FieldMapper):
    def get_field_data(self, object):
        return f'Direct Payment - ' +object.get('meta',{}).get("account_mode", "") if object.get('payment_method') == models.order.order.PAYMENT_METHOD_DIRECT else super().get_field_data(object)

class LastFiveDigitMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('meta',{}).get(self.field_name, '') if not object.get('meta',{}).get(self.field_name, '') else object.get('meta',{}).get('receipt_image', '')

class TotalMapper(FieldMapper):
    def get_field_data(self, object):
        return int(super().get_field_data(object)) if object.get('decimal_places') == 0 else super().get_field_data(object)

class OrderProductsNameMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('order_products',{}).get('name')

class OrderProductsPriceMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('order_products',{}).get('price')

class OrderProductsQtyMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('order_products',{}).get('qty')

class OrderProductsSubtotalMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('order_products',{}).get('subtotal')

class OrderProductsOrderCodeMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('order_products',{}).get('order_code')

class OrderProductsSKUMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('order_products',{}).get('sku')

class TotalMapper(FieldMapper):
    def get_field_data(self, object):
        return int(super().get_field_data(object)) if object.get('decimal_places') == 0 else super().get_field_data(object)

class ShippingCostMapper(FieldMapper):
    def get_field_data(self, object):
        if object.get('meta',{}).get('subtotal_over_free_delivery_threshold') or object.get('meta',{}).get('items_over_free_delivery_threshold'):
            return 0
        else:
            return super().get_field_data(object)

class PlatformInstanceMapper(FieldMapper):

    def __init__(self, field_name='', title='', i18n_key=None, width=None, i18n_text=None, first_only=False, **kwargs):
        super().__init__(field_name, title, i18n_key, width, i18n_text, first_only, **kwargs)
        self.cache = {}

    def get_field_data(self, object):
        platform_name = object.get('platform')
        platform_id = object.get('platform_id')
        
        if not platform_name:
            return ''
        if platform_name+str(platform_id) in self.cache:
            platform_instance = self.cache.get(platform_name+str(platform_id))
        else:
            platform_model = models.user.user_subscription.PLATFORM_ATTR.get(platform_name,{}).get('model',None)
            if not platform_model:
                return ''
            
            if not platform_model.objects.filter(id = platform_id).exists():
                return ''
            
            platform_instance = platform_model.objects.get(id = platform_id) 
            self.cache[platform_name+str(platform_id)] = platform_instance
        
        return platform_instance.name
    
class SHCPointsExportProcessor(DefaultPointsExportProcessor):
    field_mappers = [
            FieldMapper('id','Customer ID', width=15, first_only=True),
            FieldMapper('name','Name', width=30, first_only=True),
            FieldMapper('email','Email', width=50, first_only=True),
            FieldMapper('','', width=10, first_only=True),
            FieldMapper('points','Points', width=10, first_only=True),

            # FieldMapper('shipping_property_type','Residential Type', width=10, first_only=True),
            # DateTimeMapper('shipping_date_time','Delivery Date', width=20, first_only=True),
            # FieldMapper('shipping_time_slot','Delivery Time Range', width=20, first_only=True),
            # FieldMapper('platform', 'Platform', width=15, first_only=True),
            # FieldMapper('customer_name', 'Name', width=20, first_only=True, i18n_key=''),
            # FieldMapper('shipping_first_name', 'Shipping Name', width=20, first_only=True),
            # FieldMapper('remark', 'Remark', width=20, first_only=True),
            # FieldMapper('shipping_cellphone', 'Shipping Phone', width=20, first_only=True),
            # DeliveryInfonMapper('shipping_address_1', 'Shipping Address 1', width=40, first_only=True),
            # DeliveryInfonMapper('shipping_postcode', 'Postcode', width=20, first_only=True),
            # FieldMapper('shipping_region', 'Shipping Region', width=20, first_only=True),
            # FieldMapper('shipping_remark', 'Shipping Remark', width=20, first_only=True),
            # FieldMapper('shipping_email', 'E-mail', width=40, first_only=True),
            # #residentail type
            # OrderProductsSKUMapper('order_product_sku', 'SKU Code', width=20),
            # OrderProductsOrderCodeMapper('order_product_order_code', 'Product Keyword', width=20),
            # #product keyword
            # OrderProductsNameMapper('order_product_name', 'Product Name', width=40),
            # OrderProductsPriceMapper('order_product_price', 'Product Price', width=20),
            # OrderProductsQtyMapper('order_product_qty', 'Qty', width=20),
            # OrderProductsSubtotalMapper('order_product_subtotal', 'Total Price', width=20),
            # FieldMapper('subtotal', 'After Total Sum', width=20, first_only=True),
            # ShippingCostMapper('shipping_cost', 'Shipping ', width=20, first_only=True),
            # FieldMapper('total', 'Total ', width=20, first_only=True),
            # FieldMapper('payment_status', 'Payment Status', width=20, first_only=True),
            # DateTimeMapper('paid_at', 'Payment Date', width=40, first_only=True),


            # DateTimeMapper('shipping_date_time','Delivery Date', width=20, first_only=True),
            # FieldMapper('shipping_time_slot','Delivery Time Range', width=20, first_only=True),
            # FieldMapper('platform', 'Platform', width=15, first_only=True),
            # PlatformInstanceMapper('platform_instance_name', 'Platform Name', width=20, first_only=False),
            # FieldMapper('id','OrderNo', width=10, first_only=False),
            # FieldMapper('customer_name', 'Name', width=20, first_only=False),
            # FieldMapper('shipping_first_name', 'Shipping Name', width=20, first_only=False),
            # FieldMapper('shipping_cellphone', 'Shipping Phone', width=20, first_only=False),
            # DeliveryInfonMapper('shipping_address_1', 'Shipping Address 1', width=40, first_only=False),
            # DeliveryInfonMapper('shipping_postcode', 'Postcode', width=20, first_only=False),
            # FieldMapper('shipping_property_type','Residential Type', width=10, first_only=True),
            # FieldMapper('shipping_remark', 'Shipping Remark', width=20, first_only=True),
            # FieldMapper('shipping_email', 'E-mail', width=40, first_only=True),
            # OrderProductsSKUMapper('order_product_sku', 'SKU Code', width=20),
            # OrderProductsOrderCodeMapper('order_product_order_code', 'Product Keyword', width=20),
            # OrderProductsNameMapper('order_product_name', 'Product Name', width=40),
            # OrderProductsQtyMapper('order_product_qty', 'Qty', width=20),
            # OrderProductsSubtotalMapper('order_product_subtotal', 'Total Price', width=20),
            # FieldMapper('subtotal', 'After Total Sum', width=20, first_only=True),
            # ShippingCostMapper('shipping_cost', 'Shipping ', width=20, first_only=True),
            # FieldMapper('total', 'Total ', width=20, first_only=True),
            # FieldMapper('payment_status', 'Payment Status', width=20, first_only=True),
            # DateTimeMapper('paid_at', 'Payment Date', width=40, first_only=True),


        ]
