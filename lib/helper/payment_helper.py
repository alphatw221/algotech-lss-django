from math import floor

def transform_payment_amount(amount, decimal_places, price_unit):
    
    amount = __to_decimal_places(amount, decimal_places)
    amount = amount*int(price_unit)
    return amount


def __to_decimal_places(amount , decimal_places):
    return floor((amount * (10 ** decimal_places))) / (10 ** decimal_places)