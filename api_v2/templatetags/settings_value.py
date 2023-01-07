from django import template
from django.conf import settings
from datetime import datetime
import math
 
register = template.Library()
 
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

@register.simple_tag
def adjust_decimal_places(num , decimal_places):
  if decimal_places == 0:
    return math.floor((num * (10 ** decimal_places))) // (10 ** decimal_places)
  else:
    return math.floor((num * (10 ** decimal_places))) / (10 ** decimal_places)

@register.simple_tag
def get_price_unit(num):
    price_unit={
            "1":"",
            "1000":"K",
            "1000000":"M"}
    return price_unit[num]

@register.simple_tag
def discount_code(order):
    if 'code' not in order.applied_discount:
        return ''
    else:
        return str(order.applied_discount['code'])

@register.simple_tag
def get_meta(order, value):
    return order.meta.get(value,"")

@register.simple_tag
def check_free_delivery(order):
    if order.meta.get('subtotal_over_free_delivery_threshold') == True:
        return True
    elif order.meta.get('items_over_free_delivery_threshold') == True:
        return True
    elif order.free_delivery == True:
        return True
    else:
        return False

@register.simple_tag
def get_order_products(order):
    return order.order_products.all()