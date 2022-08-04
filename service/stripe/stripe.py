from django.conf import settings
import stripe
import urllib

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
    except Exception:
        print(traceback.format_exc())
        return False

def retrieve_payment_intent(api_key:str, payment_intent_id:str):

    try:
        stripe.api_key = settings.STRIPE_API_KEY
        return stripe.PaymentIntent.retrieve(payment_intent_id)     
    except Exception:
        return False

    