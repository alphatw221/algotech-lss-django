from django.conf import settings
from rest_framework.response import Response
import stripe
import urllib

import lib

import traceback
def create_checkout_session(secret, currency, order, success_url, cancel_url):
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
                unit_amount=int(product.get('price',0)*100),
                currency=currency,
            )
            items.append(
                {
                    'price': price.id,
                    "quantity": product.get('qty',0)
                },
            )

        discounts = []
        if order.adjust_price:
            discount = stripe.Coupon.create(
                amount_off=int(-order.adjust_price * 100),
                currency=currency
            )
            discounts.append(
                {
                    'coupon': discount.id,
                }
            )

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
                    'amount': int(order.shipping_cost * 100),
                    'currency': currency,
                }
            )
            shipping_options.append(
                {
                    'shipping_rate': shipping_rate.id,
                }
            )

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
        raise lib.error_handle.error.api_error.ApiCallerError('Card has been declined')
    except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
        raise lib.error_handle.error.api_error.ApiCallerError('Call Stripe api too frequently')
    except stripe.error.InvalidRequestError as e:
        if e.code == 'parameter_invalid_integer':
            raise lib.error_handle.error.api_error.ApiCallerError('Stripe only accept amount greater than or equal to 1, Please contact to our customer service.')
        raise lib.error_handle.error.api_error.ApiCallerError('Invalid parameters')
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        raise lib.error_handle.error.api_error.ApiCallerError('Authentication failed')
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        raise lib.error_handle.error.api_error.ApiCallerError('Network error')
    except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
        raise lib.error_handle.error.api_error.ApiCallerError('Stripe error')
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        raise lib.error_handle.error.api_error.ApiCallerError('No related with this payment')


def retrieve_payment_intent(api_key:str, payment_intent_id:str):

    try:
        stripe.api_key = settings.STRIPE_API_KEY
        return stripe.PaymentIntent.retrieve(payment_intent_id)     
    except Exception:
        return False

    