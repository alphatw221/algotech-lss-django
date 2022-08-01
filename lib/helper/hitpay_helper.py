
import hmac
import hashlib
import base64

KEY_LIST = ['amount', 'currency', 'payment_id', 'payment_request_id', 'phone', 'reference_number', 'status']

def is_request_valid(request, salt:str, _hmac):
    try:
        data=''
        for key in KEY_LIST:
            data.join(request.data.get(key,''))

        temp = hmac.new(salt.encode(), msg=data.encode(), digestmod=hashlib.sha256).digest()
        return _hmac == base64.b64encode(temp).decode() 
    except Exception as e:
        print(e)
        return False