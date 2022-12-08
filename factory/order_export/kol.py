import lib
from api import models
from lib.helper.xlsx_helper import FieldMapper
from .default import DefaultOrderExportProcessor

from dateutil import parser


class DateTimeMapper(FieldMapper):
    def get_field_data(self, object):
        return parser.parse(super().get_field_data(object)).strftime("%Y-%m-%d")


class OrderIdMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('id')

class OrderProductSuggestedPriceMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('price_ori_subtotal')
    
class OrderSubtotalMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('subtotal')

class OrderAppliedDiscountMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('discount')
    
class OrderPointDiscountMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('point_discount')
    
class OrderAjustPriceMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('adjust_price')
    
class OrderGrossMapper(FieldMapper):
    def get_field_data(self, object):
        return object.get('gross')



class KOLOrderExportProcessor(DefaultOrderExportProcessor):

    field_mappers = [
        OrderIdMapper('id', 'Order ID', width=20),
        OrderProductSuggestedPriceMapper('price_ori_subtotal', 'Product Suggested Price Subtotal', width=30),
        OrderSubtotalMapper('subtotal', 'Product Selling Price Subtotal', width=30),
        OrderAppliedDiscountMapper('discount', 'Normal Discount', width=20),
        OrderPointDiscountMapper('point_discount', 'Point Discount', width=20),
        OrderAjustPriceMapper('adjust_price', 'Adjust Price', width=20),
        OrderGrossMapper('gross', 'Gross', width=20)
    ]