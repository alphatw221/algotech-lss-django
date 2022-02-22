from dataclasses import dataclass
from backend.api._api_caller import RestApiJsonCaller
from django.conf import settings


#     # domain_url: str = "https://test.ipg-online.com/connect/gateway/processing"3

# class IPG_Helper:

#     @dataclass
#     class IPGApiCaller(RestApiJsonCaller):
#         domain_url: str = "https://test.ipg-online.com"

#     storename="4530042983"
#     sharedSecret="Xe33QM7UTs"
#     responseSuccessURL = "http://104.199.211.63/api/test"
#     responseFailURL = "http://104.199.211.63/api/test"

#     @classmethod
#     def create_payment(cls, timezone, chargetotal, currency):
#         txndatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         payment_hash=hashlib.sha256((cls.storename + str(txndatetime) + str(chargetotal) + cls.sharedSecret).encode('utf-8')).hexdigest()
#         data={
#             "storename":cls.storename,
#             "txntype":"sale",
#             "mode":"payonly",
#             "timezone":timezone,
#             "txndatetime": txndatetime,
#             "hash_algorithm":"SHA256",
#             "hash":payment_hash,
#             "chargetotal":chargetotal,
#             "currency":currency,
#             "responseSuccessURL":cls.responseSuccessURL,
#             "responseFailURL":cls.responseFailURL
#         }
#         print(data)
#         # this->storeId . $this->txndatetime . $this->chargetotal . $this->currency . $this->sharedSecret;

#         # ret = cls.IPGApiCaller("connect/gateway/processing",data=data).post()
#         # print(ret)


# class node:
#     number=None
#     left:node = None
#     right:node = None


# class solution:

#     sum=0

#     def h(node, l):
#         if not node:
#             return
#         if not node.left and node.right and l:
#             sum += node.number
#         else:
#             h(node.right,False)
#             h(node.left,True)



class HitPay_Helper:

    @dataclass
    class HitPayApiCaller(RestApiJsonCaller):
        domain_url: str = settings.HITPAY_API_URL
