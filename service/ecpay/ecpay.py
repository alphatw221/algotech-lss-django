# import importlib.util
# spec = importlib.util.spec_from_file_location(
#     "ecpay_payment_sdk",
#     "payment_sdk.py"
# )
# module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(module)
import traceback
from .payment_sdk import ECPayPaymentSdk
from .invoice_sdk import EcpayInvoice
from .logistic_sdk import ECPayLogisticSdk
from datetime import datetime
import time
import random


# action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
action_url = 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5' # 正式環境
# Invoice_Url = 'https://einvoice-stage.ecpay.com.tw/Invoice/Issue'
Invoice_Url = 'https://einvoice.ecpay.com.tw/B2CInvoice/Issue'



def create_order(merchant_id, hash_key, hash_iv,payment_amount, order, return_url, order_result_url):
    
    # item_name = ''
    # for item in order.products:
    #     print(order.products)
    #     item_name += f'#{dict(order.products[item])["name"]}'
    params = {
    'MerchantTradeNo': str(order.id)+datetime.now().strftime("%Y%m%d") ,
    'StoreID': '',
    'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
    'PaymentType': 'aio',
    'TotalAmount': payment_amount,
    'TradeDesc': 'test order',
    'ItemName': 'Order#',
    'ReturnURL': str(return_url),
    'ChoosePayment': 'ALL',
    'ClientBackURL': 'https://www.ecpay.com.tw/client_back_url.php',
    'ItemURL': 'https://www.ecpay.com.tw/item_url.php',
    'Remark': '',
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
        print(params)
        final_order_params = ecpay_payment_sdk.create_order(params)

        # 產生 html 的 form 格式
        # action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
        action_url = 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5' # 正式環境
        html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)
        # return action_url,final_order_params
       
        return action_url,final_order_params
    except Exception as error:
        print('An exception happened: ' + str(error))
        

def create_register_order(merchant_id, hash_key, hash_iv,payment_amount:int,plan:str, return_url, order_result_url):
    try:
        params = {
        'MerchantTradeNo': str(random.randint(0,1000))+str(datetime.now().strftime("%Y%m%d%H%M")) ,
        'StoreID': '',
        'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        'PaymentType': 'aio',
        'TotalAmount': payment_amount,
        'TradeDesc': 'test order',
        'ItemName': plan,
        'ReturnURL': str(return_url),
        'ChoosePayment': 'ALL',
        'ClientBackURL': '',
        'ItemURL': '',
        'Remark': '',
        'ChooseSubPayment': '',
        'OrderResultURL': str(order_result_url),
        'NeedExtraPaidInfo': 'Y',
        'DeviceSource': '',
        'IgnorePayment': '',
        'PlatformID': '',
        'InvoiceMark': 'N',
        'EncryptType': 1,
        }
        
        ecpay_payment_sdk = ECPayPaymentSdk(
            MerchantID=merchant_id,
            HashKey=hash_key,
            HashIV=hash_iv
        )

        # 產生綠界訂單所需參數
        final_order_params = ecpay_payment_sdk.create_order(params)

        # 產生 html 的 form 格式
        # action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
        action_url = 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5' # 正式環境
        html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)

        return True, action_url, final_order_params
    except Exception:
        print(traceback.format_exc())
    return False, None, None

def check_mac_value(merchant_id,hash_key,hash_iv,params):
    
    ecpay_payment_sdk = ECPayPaymentSdk(
        MerchantID=merchant_id,
        HashKey=hash_key,
        HashIV=hash_iv
    )
    
    check_value = ecpay_payment_sdk.generate_check_value(params)
    
    return check_value


def order_create_invoice(merchant_id,hash_key,hash_iv,order,amount):
    ecpay_invoice = EcpayInvoice()
    
    ecpay_invoice.Invoice_Method = 'INVOICE'
    ecpay_invoice.Invoice_Url = Invoice_Url
    ecpay_invoice.MerchantID = merchant_id
    ecpay_invoice.HashKey = hash_key
    ecpay_invoice.HashIV = hash_iv
    # ecpay_invoice.MerchantID = '2000132'
    # ecpay_invoice.HashKey = 'ejCk326UnaZWKisg'
    # ecpay_invoice.HashIV = 'q9jcZX8Ib9LM8wYk'
    
    ecpay_invoice.Send['Items'].append({
        'ItemName': order.campaign.title,
        'ItemCount': 1,
        'ItemWord': 'x1',
        'ItemPrice': amount,
        'ItemTaxType': '',
        'ItemAmount': amount,
        'ItemRemark': ''
    })
    
    RelateNumber = 'ECPAY' + time.strftime("%Y%m%d%H%M%S", time.localtime())  # 產生測試用自訂訂單編號
    ecpay_invoice.Send['RelateNumber'] = RelateNumber
    ecpay_invoice.Send['CustomerID'] = ''
    ecpay_invoice.Send['CustomerIdentifier'] = ''
    ecpay_invoice.Send['CustomerName'] = order.shipping_last_name+order.shipping_first_name
    ecpay_invoice.Send['CustomerAddr'] = 'address'
    ecpay_invoice.Send['CustomerPhone'] = ''
    ecpay_invoice.Send['CustomerEmail'] = order.shipping_email
    ecpay_invoice.Send['ClearanceMark'] = ''
    ecpay_invoice.Send['Notify'] = 'E'
    ecpay_invoice.Send['Print'] = '1'
    ecpay_invoice.Send['Donation'] = '0'
    ecpay_invoice.Send['LoveCode'] = ''
    ecpay_invoice.Send['CarruerType'] = ''
    ecpay_invoice.Send['CarruerNum'] = ''
    ecpay_invoice.Send['TaxType'] = '1'
    ecpay_invoice.Send['SalesAmount'] = amount
    ecpay_invoice.Send['InvoiceRemark'] = 'SDK TEST Python V1.0.6'
    ecpay_invoice.Send['InvType'] = '07'
    ecpay_invoice.Send['vat'] = '1'

    # 4. 送出
    print(ecpay_invoice)
    aReturn_Info = ecpay_invoice.Check_Out()

    # 5. 返回
    print('RelateNumber:' + str(RelateNumber))
    print(aReturn_Info)
    print(aReturn_Info['RtnMsg'])
    print('發票號碼：' + aReturn_Info['InvoiceNumber'])
    
    return aReturn_Info

def register_create_invoice(merchant_id,hash_key,hash_iv,user_register,amount):
    ecpay_invoice = EcpayInvoice()
    
    ecpay_invoice.Invoice_Method = 'INVOICE'
    ecpay_invoice.Invoice_Url = Invoice_Url
    ecpay_invoice.MerchantID = merchant_id
    ecpay_invoice.HashKey = hash_key
    ecpay_invoice.HashIV = hash_iv
    
    ecpay_invoice.Send['Items'].append({
        'ItemName': user_register['type'],
        'ItemCount': 1,
        'ItemWord': 'x1',
        'ItemPrice': amount,
        'ItemTaxType': '',
        'ItemAmount': amount,
        'ItemRemark': ''
    })
    
    RelateNumber = 'ECPAY' + time.strftime("%Y%m%d%H%M%S", time.localtime())  # 產生測試用自訂訂單編號
    ecpay_invoice.Send['RelateNumber'] = RelateNumber
    ecpay_invoice.Send['CustomerID'] = ''
    ecpay_invoice.Send['CustomerIdentifier'] = ''
    ecpay_invoice.Send['CustomerName'] = user_register['name']
    ecpay_invoice.Send['CustomerAddr'] = 'address'
    ecpay_invoice.Send['CustomerPhone'] = ''
    ecpay_invoice.Send['CustomerEmail'] = user_register['email']
    ecpay_invoice.Send['ClearanceMark'] = ''
    ecpay_invoice.Send['Notify'] = 'E'
    ecpay_invoice.Send['Print'] = '1'
    ecpay_invoice.Send['Donation'] = '0'
    ecpay_invoice.Send['LoveCode'] = ''
    ecpay_invoice.Send['CarruerType'] = ''
    ecpay_invoice.Send['CarruerNum'] = ''
    ecpay_invoice.Send['TaxType'] = '1'
    ecpay_invoice.Send['SalesAmount'] = amount
    ecpay_invoice.Send['InvoiceRemark'] = ''
    ecpay_invoice.Send['InvType'] = '07'
    ecpay_invoice.Send['vat'] = '1'

    # 4. 送出
    aReturn_Info = ecpay_invoice.Check_Out()

    # 5. 返回
    print('RelateNumber:' + str(RelateNumber))
    print(aReturn_Info)
    print(aReturn_Info['RtnMsg'])
    print('發票號碼：' + aReturn_Info['InvoiceNumber'])
    
    return aReturn_Info

def cvs_map(cart_oid,merchant_id,hash_key,hash_iv,logistics_sub_type,server_reply_url):
    # FAMIC2C 
    MerchantTradeNo = 'ECPAY' + time.strftime("%Y%m%d%H%M%S", time.localtime())
    cvs_map_params = {
        "MerchantTradeNo": MerchantTradeNo,
        "LogisticsType": "CVS",
        # 若申請類型為 B2C，只能串參數為 FAMI、UNIMART、HILIFE
        # 若申請類型為 C2C，只能串參數為 FAMIC2C、UNIMARTC2C、HILIFEC2C
        "LogisticsSubType": logistics_sub_type,
        "IsCollection": "Y",
        "ServerReplyURL": server_reply_url,
        "ExtraData": cart_oid,
        "Device": 0,
    }

    # 建立實體
    ecpay_logistic_sdk = ECPayLogisticSdk(
        MerchantID=merchant_id,
        HashKey=hash_key,
        HashIV=hash_iv
    )

    try:
        # 產生綠界物流訂單所需參數
        final_params = ecpay_logistic_sdk.cvs_map(cvs_map_params)

        # 產生 html 的 form 格式
        #action_url = 'https://logistics-stage.ecpay.com.tw/Express/map'  # 測試環境
        action_url = 'https://logistics.ecpay.com.tw/Express/map' # 正式環境
        html = ecpay_logistic_sdk.gen_html_post_form(action_url, final_params)
        return action_url,final_params
    except Exception as error:
        print('An exception happened: ' + str(error))
        

def create_shipping_order(order,server_reply_url,sub_data={}):
    print(sub_data)
    MerchantTradeNo = str(order.id) + time.strftime("%Y%m%d%H%M%S", time.localtime())
    campaign = order.campaign
    create_shipping_order_params = {
        'MerchantTradeNo': MerchantTradeNo,
        'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        'LogisticsType': order.shipping_option_data.get('logisticsType'), #HOME or CVS
        'GoodsAmount': int(order.total),
        'CollectionAmount': int(order.total),
        'GoodsName': 'LSS Order',
        'SenderName': campaign.meta_logistic['ecpay']['sender_name'],
        'SenderPhone': campaign.meta_logistic['ecpay']['sender_phone'], #campaign data
        'SenderCellPhone': campaign.meta_logistic['ecpay']['sender_phone'],
        'ReceiverName': str(order.shipping_first_name) + str(order.shipping_last_name),
        'ReceiverPhone': order.shipping_phone,
        'ReceiverCellPhone': order.shipping_phone,
        'ReceiverEmail': order.shipping_email,
        'TradeDesc': 'lss',
        'ServerReplyURL': server_reply_url,
        'ClientReplyURL': '',
        'Remark': '',
        'PlatformID': '',
        'LogisticsC2CReplyURL': '',
    }

    update_params = {}
    if order.shipping_option_data.get('logisticsType') == 'CVS':
        update_params = {
            'IsCollection': sub_data.get('is_collection', 'N'),
            'LogisticsSubType': order.meta.get('ecpay_cvs',{}).get('logistics_sub_type'), #[TCAT POST][FAMIC2C UNIMARTC2C]
            'ReceiverStoreID': order.meta.get('ecpay_cvs',{}).get('cvs_store_id'),
            #TODO #setting seller return store
            'ReturnStoreID':  campaign.meta_logistic['ecpay']['return_store_id'], #返回之超商店號
            'SenderName': "Ｎick .L"
        }
    elif order.shipping_option_data.get('logisticsType') == 'HOME':
        update_params = {
            'IsCollection': 'N',
            'LogisticsSubType': 'TCAT', #[TCAT POST][FAMIC2C UNIMARTC2C]
            'SenderZipCode': campaign.meta_logistic['ecpay']['sender_zip_code'],
            'SenderAddress': campaign.meta_logistic['ecpay']['sender_address'],
            'ReceiverZipCode': order.shipping_postcode,
            'ReceiverAddress': order.shipping_location + order.shipping_address_1,
            'Temperature': '0001', #0001:常溫 (預設值) 0002:冷藏 0003:冷凍 [*POST必為0001]
            'Distance': '00', #00:同縣市 (預設值) 01:外縣市 02:離島 會自動調整 [*POST忽略]
            'Specification': '0001', #0001: 60cm (預設值) 0002: 90cm 0003: 120cm 0004: 150cm [*POST忽略]
            'ScheduledPickupTime': '4', #[*POST忽略]
            'ScheduledDeliveryTime': '4', #1: 13點前 2: 14點~18點 3: 14點~18點 4:不限時 [*POST忽略]
            'ScheduledDeliveryDate': '',
            'PackageCount': '',
        }

    # 更新及合併參數
    create_shipping_order_params.update(update_params)

    # 建立實體
    ecpay_logistic_sdk = ECPayLogisticSdk(
        MerchantID=campaign.meta_logistic['ecpay']['merchant_id'],
        HashKey=campaign.meta_logistic['ecpay']['hash_key'],
        HashIV=campaign.meta_logistic['ecpay']['hash_iv']
        # C2C test
        # MerchantID='2000933',
        # HashKey='XBERn1YOvpM9nfZc',
        # HashIV='h1ONHk4P4yqbl5LK'
        
        #HOME test
        # MerchantID='2000132',
        # HashKey='5294y06JbISpM5x9',
        # HashIV='v77hoKGq4kWxNNIS'
    )

    try:
        # 介接路徑
        # action_url = 'https://logistics-stage.ecpay.com.tw/Express/Create'  # 測試環境
        action_url = 'https://logistics.ecpay.com.tw/Express/Create' # 正式環境

        # print(create_shipping_order_params)
        # 建立物流訂單並接收回應訊息
        reply_result = ecpay_logistic_sdk.create_shipping_order(
            action_url=action_url,
            client_parameters=create_shipping_order_params)
        return reply_result

    except Exception as error:
        print('An exception happened: ' + str(error))