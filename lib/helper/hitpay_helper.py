
import hmac
import hashlib
import base64

KEY_LIST = ['amount', 'currency', 'payment_id', 'payment_request_id', 'phone', 'reference_number', 'status']

def is_request_valid(request, salt:str, _hmac):
    try:
        print('request:\n')
        print(request.data.dict())

           # {'payment_id': '96ec6ec3-fea0-4a9d-bd38-0b9bb05b1f24', 
        # 'payment_request_id': '96ec6ec3-2dcb-4aca-ad54-d29fde47a3c3', 
        # 'phone': '', 
        # 'amount': '1.00', 
        # 'currency': 'SGD', 
        # 'status': 'completed', 
        # 'reference_number': '32846',
        #  'hmac': 'bcf1e64ffd1214f3af65202dc2072b221c25fdc221b540559b7d563f5a454b8d'}

        print('hmac:\n')
        print(_hmac)
        # bcf1e64ffd1214f3af65202dc2072b221c25fdc221b540559b7d563f5a454b8d

        data=''
        for key in KEY_LIST:
            data = data+request.data.get(key,'')
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