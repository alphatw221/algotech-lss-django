import lib
from api import models
from lib.helper.xlsx_helper import FieldMapper
from .default import DefaultOrderExportProcessor
from django.utils.translation import ugettext as _

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
        return object.get('profit')



class KOLOrderExportProcessor(DefaultOrderExportProcessor):

    field_mappers = [
        OrderIdMapper(field_name='id', title="order_id", width=20),
        OrderSubtotalMapper(field_name='subtotal', title="subtotal", width=30),
        OrderProductSuggestedPriceMapper(field_name='price_ori_subtotal', title="price_ori_subtotal", width=30),
        # OrderAppliedDiscountMapper(field_name='discount', title="discount_promo_code", width=20),
        # OrderPointDiscountMapper(field_name='point_discount', title="discount_point", width=20),
        # OrderAjustPriceMapper(field_name='adjust_price', title="adjust_price", width=20),
        OrderGrossMapper(field_name='profit', title="profit", width=20)
    ]