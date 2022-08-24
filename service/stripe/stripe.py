from django.conf import settings
from rest_framework.response import Response
import stripe
import urllib

import lib

import traceback


from math import floor

def __transform_payment_amount(amount, decimal_places, price_unit):
    
    amount = __to_decimal_places(amount, decimal_places)
    amount = amount*int(price_unit)
    return amount


def __to_decimal_places(amount , decimal_places):
    return floor((amount * (10 ** decimal_places))) / (10 ** decimal_places)


def create_checkout_session(secret, currency, order, decimal_places, price_unit, success_url, cancel_url):
    try:
        stripe.api_key = secret
        items = []
        for key, product in order.products.items():
            stripe_product = stripe.Product.create(
                name=product.get('name',''),
                images=[urllib.parse.quote(f"{settings.GS_URL}{product.get('image','')}").replace("%3A", ":")]
            )
            
            price = stripe.Price.create(
                product=stripe_product.id,
                unit_amount=int(__transform_payment_amount(product.get('price'), decimal_places, price_unit)*100),
                currency=currency,
            )
            print('product')
            print(int(__transform_payment_amount(product.get('price'), decimal_places, price_unit)*100))
            items.append(
                {
                    'price': price.id,
                    "quantity": product.get('qty',0)
                },
            )

        discounts = []
        if order.adjust_price:
            discount = stripe.Coupon.create(
                amount_off=int(-__transform_payment_amount(order.adjust_price, decimal_places, price_unit) * 100),
                currency=currency
            )
            discounts.append(
                {
                    'coupon': discount.id,
                }
            )
            print('adjuct')
            print(int(-__transform_payment_amount(order.adjust_price, decimal_places, price_unit) * 100))

        if order.discount:
            discount = stripe.Coupon.create(
                amount_off=int(__transform_payment_amount(order.discount, decimal_places, price_unit) * 100),
                currency=currency
            )
            discounts.append(
                {
                    'coupon': discount.id,
                }
            )
            print('discount')
            print(int(-__transform_payment_amount(order.discount, decimal_places, price_unit) * 100))



        shipping_options = []


        if order.free_delivery or order.meta.get('subtotal_over_free_delivery_threshold') or order.meta.get('items_over_free_delivery_threshold'):
            shipping_rate = stripe.ShippingRate.create(
                display_name="Free Delivery",
                type="fixed_amount",
                fixed_amount={
                    'amount': 0,
                    'currency': currency,
                }
            )
            shipping_options.append(
                {
                    'shipping_rate': shipping_rate.id,
                }
            )
        else :
            shipping_rate = stripe.ShippingRate.create(
                display_name="General Shipping",
                type="fixed_amount",
                fixed_amount={
                    'amount': int( __transform_payment_amount(order.shipping_cost, decimal_places, price_unit) * 100),
                    'currency': currency,
                }
            )
            shipping_options.append(
                {
                    'shipping_rate': shipping_rate.id,
                }
            )
        print('shipping')
        print(int( __transform_payment_amount(order.shipping_cost, decimal_places, price_unit) * 100))
        checkout_session = stripe.checkout.Session.create(
            line_items=items,
            shipping_options=shipping_options,
            discounts=discounts,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        

        return checkout_session
    except Exception:
        print(traceback.format_exc())
        return False


def is_payment_successful(secret, session_id):
    try:
        stripe.api_key = secret
                
        session = stripe.checkout.Session.retrieve(session_id)
        payment_intent = stripe.PaymentIntent.retrieve(
            session.payment_intent,
        )
        if payment_intent.status == "succeeded":
            return True, payment_intent

        return False, None
    except Exception:
        return False, None


def create_payment_intent(api_key:str,  amount:float, currency:str, receipt_email:str):
    try:
        stripe.api_key = api_key
        return stripe.PaymentIntent.create( amount=int(amount*100), currency=currency, receipt_email=receipt_email)        
    except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
        print ('Status, Code, Param, Message', e.http_status, e.code, e.param, e.user_message)
        raise lib.error_handle.error.api_error.ApiCallerError('stripe.card_error')
    except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
        raise lib.error_handle.error.api_error.ApiCallerError('stripe.rate_limit_error')
    except stripe.error.InvalidRequestError as e:
        if e.code == 'parameter_invalid_integer':
            raise lib.error_handle.error.api_error.ApiCallerError('stripe.invalid_request_error.invalid_integer')
        raise lib.error_handle.error.api_error.ApiCallerError('stripe.invalid_request_error.invalid_parameters')
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        raise lib.error_handle.error.api_error.ApiCallerError('stripe.authentication_error')
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        raise lib.error_handle.error.api_error.ApiCallerError('stripe.api_connection_error')
    except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
        raise lib.error_handle.error.api_error.ApiCallerError('stripe.stripe_error')
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        raise lib.error_handle.error.api_error.ApiCallerError('stripe.no_related_error')


def retrieve_payment_intent(api_key:str, payment_intent_id:str):

    try:
        stripe.api_key = settings.STRIPE_API_KEY
        return stripe.PaymentIntent.retrieve(payment_intent_id)     
    except Exception:
        return False

    