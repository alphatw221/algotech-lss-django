
import hmac
import hashlib
import base64

KEY_LIST = ['amount', 'currency', 'payment_id', 'payment_request_id', 'phone', 'reference_number', 'status']

def is_request_valid(request, salt:str, _hmac:str):
    try:
        data=''
        for key in KEY_LIST:
            data = data+(key+request.data.get(key,''))
            
        hexdig = hmac.new(salt.encode(), msg=data.encode(), digestmod=hashlib.sha256).hexdigest()
        return _hmac == hexdig
    except Exception as e:
        return False