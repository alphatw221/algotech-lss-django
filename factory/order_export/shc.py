from .default import DefaultOrderExportProcessor

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


class TotalMapper(FieldMapper):
    def get_field_data(self, object):
        return int(super().get_field_data(object)) if object.get('decimal_places') == 0 else super().get_field_data(object)





class SHCOrderExportProcessor(DefaultOrderExportProcessor):
    field_mappers = [
            FieldMapper('id','OrderNo', width=10, first_only=True),
            FieldMapper('platform', 'Platform', width=15, first_only=True),
            FieldMapper('customer_name', 'Name', width=20, first_only=True),
            FieldMapper('shipping_cellphone', 'Shipping Phone', width=20, first_only=True),
            DeliveryInfonMapper('shipping_address_1', 'Shipping Address 1', width=40, first_only=True),
            DeliveryInfonMapper('shipping_postcode', 'Postcode', width=20, first_only=True),
            FieldMapper('shipping_email', 'E-mail', width=40, first_only=True),
            #residentail type
            FieldMapper('sku', 'SKU Code', width=20),
            #product keyword
            OrderProductsNameMapper('order_product_name', 'Product Name', width=40),
            OrderProductsPriceMapper('order_product_price', 'Product Price', width=20),
            OrderProductsQtyMapper('order_product_qty', 'Qty', width=20),
            OrderProductsSubtotalMapper('order_product_subtotal', 'Total Price', width=20),
            FieldMapper('subtotal', 'After Total Sum', width=20, first_only=True),
            FieldMapper('payment_status', 'Payment Status', width=20, first_only=True),
            DateTimeMapper('paid_at', 'Payment Date', width=40, first_only=True)

        ]
