
import hmac
import hashlib
import base64

KEY_LIST = ['amount', 'currency', 'payment_id', 'payment_request_id', 'phone', 'reference_number', 'status']

def is_request_valid(request, salt:str, _hmac):
    try:
        print('request:\n')
        print(request.data.dict())
        print('hmac:\n')
        print(_hmac)


        data=''
        for key in KEY_LIST:
            data.join(request.data.get(key,''))
        print('data:\n')
        print(data)
        dig = hmac.new(salt.encode(), msg=data.encode(), digestmod=hashlib.sha256).digest()
        hexdig = hmac.new(salt.encode(), msg=data.encode(), digestmod=hashlib.sha256).hexdigest()()

        print('dig:\n')
        print(dig)

        print('hexdig:\n')
        print(hexdig)


        print("base64\n")
        print( base64.b64encode(dig).decode())
        
        return _hmac == base64.b64encode(dig).decode() 
    except Exception as e:
        print(e)
        return False