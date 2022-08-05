import traceback
import paypalrestsdk


def create_payment(client_id, client_secret, amount, currency, return_url, cancel_url):


    try:
        paypalrestsdk.configure({
            "mode": "live",  # live mode
            "client_id": client_id,
            "client_secret": client_secret
        })
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url
            },
            "transactions": [{
                "item_list": {
                    # "items": [
                    #     {
                    #         # "name": "Cake",
                    #         # "price": "8.00",
                    #         "currency": currency,
                    #         # "quantity": 1
                    #     }
                    # ]
                },
                "amount": {
                    "total": amount,
                    "currency": currency},
                "description": "This is the payment transaction description."
            }]
        })

        if not payment.create():
            return False
        return payment
    except Exception:
        print(traceback.format_exc())
        return False

    
    
def find_payment(client_id, client_secret, paymentId):
    try:
        paypalrestsdk.configure({
            "mode": "live",  # live
            "client_id": client_id,
            "client_secret": client_secret
        })

        payment = paypalrestsdk.Payment.find(paymentId)
        return payment
    except Exception:
        return False