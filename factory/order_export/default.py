import lib
from api import models
from lib.helper.xlsx_helper import FieldMapper

from dateutil import parser


class DateTimeMapper(FieldMapper):
    def get_field_data(self, object):
        print(object)
        return super().get_field_data(object).strftime("%Y-%m-%d")


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
        return f'{models.order.order.PAYMENT_METHOD_DIRECT} - ' +object.get('meta',{}).get("account_mode", "") if object.get('payment_method') == models.order.order.PAYMENT_METHOD_DIRECT else super().get_field_data(object)

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


class TotalMapper(FieldMapper):
    def get_field_data(self, object):
        return int(super().get_field_data(object)) if object.get('decimal_places') == 0 else super().get_field_data(object)


class DefaultOrderExportProcessor:

    field_mappers = [
        FieldMapper('id','id', width=10),
        DateTimeMapper('created_at', 'created_at', width=15),
        FieldMapper('platform', 'platform', width=15),
        FieldMapper('customer_name', 'customer_name', width=20),
        ShippingNameMapper('shipping_name', 'shipping_name', width=20),
        FieldMapper('shipping_cellphone', 'shipping_cellphone', width=20),
        FieldMapper('shipping_email', 'shipping_email', width=40),
        ShippingMethodMapper('shipping_method', 'shipping_method', width=20),
        ShippingOptionMapper('shipping_option', 'shipping_option', width=20),
        DeliveryInfonMapper('shipping_address_1', 'shipping_address_1', width=40),
        DeliveryInfonMapper('shipping_location', 'shipping_location', width=20),
        DeliveryInfonMapper('shipping_region', 'shipping_region', width=20,),
        DeliveryInfonMapper('shipping_postcode', 'shipping_postcode', width=20),
        PickupStoreMapper('pick_up_store', 'pick_up_store', width=20),
        PickupAddressMapper('pickup_address', 'pickup_address', width=20),
        FieldMapper('shipping_remark', 'shipping_remark', width=20,),
        PaymentMethodMapper('payment_method', 'payment_method', width=30),
        FieldMapper('payment_status', 'payment_status', width=20),
        LastFiveDigitMapper('last_five_digit', 'last_five_digit', width=20),
        OrderProductsNameMapper('order_product_name', 'order_product_name', width=40),
        OrderProductsPriceMapper('order_product_price', 'order_product_price', width=20),
        OrderProductsQtyMapper('order_product_qty', 'order_product_qty', width=20),
        OrderProductsSubtotalMapper('order_product_subtotal', 'order_product_subtotal', width=20)
    ]

    additional_field_mappers=[]

    def __init__(self, iterable_objects, user_subscription) -> None:
        self.iterable_objects = iterable_objects
        self.user_subscription = user_subscription
        
    def export_order_data(self):

        js_xlsx_processor = lib.helper.xlsx_helper.JSXlsxProcessor(field_mappers=self.field_mappers, iterable_objects=self.iterable_objects, lang = self.user_subscription.lang, additional_field_mappers=self.additional_field_mappers)
        return js_xlsx_processor.generate_json()