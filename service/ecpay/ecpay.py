# import importlib.util
# spec = importlib.util.spec_from_file_location(
#     "ecpay_payment_sdk",
#     "payment_sdk.py"
# )
# module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(module)
from .payment_sdk import ECPayPaymentSdk
from datetime import datetime


def create_order(merchant_id, hash_key, hash_iv, amount:int, order_id, return_url, order_result_url):
    params = {
    'MerchantTradeNo': str(order_id) ,
    'StoreID': '',
    'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
    'PaymentType': 'aio',
    'TotalAmount': amount,
    'TradeDesc': 'test order',
    'ItemName': 'test1#test2',
    'ReturnURL': str(return_url),
    'ChoosePayment': 'ALL',
    'ClientBackURL': 'https://www.ecpay.com.tw/client_back_url.php',
    'ItemURL': 'https://www.ecpay.com.tw/item_url.php',
    'Remark': 'test remark',
    'ChooseSubPayment': '',
    'OrderResultURL': str(order_result_url),
    'NeedExtraPaidInfo': 'Y',
    'DeviceSource': '',
    'IgnorePayment': '',
    'PlatformID': '',
    'InvoiceMark': 'N',
    'CustomField1': '',
    'CustomField2': '',
    'CustomField3': '',
    'CustomField4': '',
    'EncryptType': 1,
    }
    
    ecpay_payment_sdk = ECPayPaymentSdk(
        MerchantID=merchant_id,
        HashKey=hash_key,
        HashIV=hash_iv
    )
    try:
        # 產生綠界訂單所需參數
        final_order_params = ecpay_payment_sdk.create_order(params)

        # 產生 html 的 form 格式
        action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
        # action_url = 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5' # 正式環境
        html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)
        # return action_url,final_order_params
        return action_url,html
    except Exception as error:
        print('An exception happened: ' + str(error))