import lib
from api import models
from lib.helper.xlsx_helper import FieldMapper

from dateutil import parser


class DateTimeMapper(FieldMapper):
    def get_field_data(self, object):
        return parser.parse(super().get_field_data(object)).strftime("%Y-%m-%d")


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


class TotalMapper(FieldMapper):
    def get_field_data(self, object):
        return int(super().get_field_data(object)) if object.get('decimal_places') == 0 else super().get_field_data(object)


class DefaultOrderExportProcessor:

    field_mappers = [
            FieldMapper('id','ID', width=10,i18n_key='REPORT/COLUMN_TITLE/ID'),
            DateTimeMapper('created_at', 'Order Date', width=15, i18n_key='REPORT/COLUMN_TITLE/ORDER_DATE'),
            FieldMapper('platform', 'Platform', width=15, i18n_key='REPORT/COLUMN_TITLE/PLATFORM'),
            FieldMapper('customer_name', 'Customer Name', width=20, i18n_key='REPORT/COLUMN_TITLE/CUSTOMER_NAME'),
            ShippingNameMapper('shipping_name', 'Shipping Name', width=20, i18n_key='REPORT/COLUMN_TITLE/SHIPPING_NAME'),
            FieldMapper('shipping_phone', 'Shipping Phone', width=20, i18n_key='REPORT/COLUMN_TITLE/SHIPPING_PHONE'),
            FieldMapper('shipping_email', 'E-mail', width=40, i18n_key='REPORT/COLUMN_TITLE/EMAIL'),
            ShippingMethodMapper('shipping_method', 'Shipping Method', width=20, i18n_key='REPORT/COLUMN_TITLE/SHIPPING_METHOD'),
            ShippingOptionMapper('shipping_option', 'Shipping Option', width=20, i18n_key='REPORT/COLUMN_TITLE/SHIPPING_OPTION'),
            DeliveryInfonMapper('shipping_address_1', 'Shipping Address 1', width=40, i18n_key='REPORT/COLUMN_TITLE/SHIPPING_ADDRESS_1'),
            DeliveryInfonMapper('shipping_location', 'Location', width=20, i18n_key='REPORT/COLUMN_TITLE/LOCATION'),
            DeliveryInfonMapper('shipping_region', 'Region', width=20, i18n_key='REPORT/COLUMN_TITLE/REGION'),
            DeliveryInfonMapper('shipping_postcode', 'Postcode', width=20, i18n_key='REPORT/COLUMN_TITLE/POSTCODE'),
            PickupStoreMapper('pick_up_store', 'Pick up Store', width=20, i18n_key='REPORT/COLUMN_TITLE/PICK_UP_STORE'),
            PickupAddressMapper('pickup_address', 'Pick up Address', width=20, i18n_key='REPORT/COLUMN_TITLE/PICK_UP_ADDRESS'),
            FieldMapper('shipping_remark', 'Remark', width=20, i18n_key='REPORT/COLUMN_TITLE/REMARK'),
            PaymentMethodMapper('payment_method', 'Payment Method', width=30, i18n_key='REPORT/COLUMN_TITLE/PAYMENT_METHOD'),
            FieldMapper('payment_status', 'Payment Status', width=20, i18n_key='REPORT/COLUMN_TITLE/PAYMENT_STATUS'),
            LastFiveDigitMapper('last_five_digit', 'Payment Record', width=20, i18n_key='REPORT/COLUMN_TITLE/PAYMENT_RECORD'),
            OrderProductsNameMapper('order_product_name', 'Product Name', width=40),
            OrderProductsPriceMapper('order_product_price', 'Product Price', width=20),
            OrderProductsQtyMapper('order_product_qty', 'Qty', width=20),
            OrderProductsSubtotalMapper('order_product_subtotal', 'Subtotal', width=20)
        ]

    def __init__(self, iterable_objects, user_subscription) -> None:
        self.iterable_objects = iterable_objects
        self.user_subscription = user_subscription
        
    def export_order_data(self):

        js_xlsx_processor = lib.helper.xlsx_helper.JSXlsxProcessor(field_mappers=self.field_mappers, iterable_objects=self.iterable_objects, lang = self.user_subscription.lang)
        return js_xlsx_processor.generate_json()