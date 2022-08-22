# import importlib.util
# spec = importlib.util.spec_from_file_location(
#     "ecpay_payment_sdk",
#     "payment_sdk.py"
# )
# module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(module)
from .payment_sdk import ECPayPaymentSdk
from .invoice_sdk import EcpayInvoice
from .logistic import data_encode
from datetime import datetime
import time


action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
# action_url = 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5' # 正式環境
Invoice_Url = 'https://einvoice-stage.ecpay.com.tw/Invoice/Issue'
# Invoice_Url = 'https://einvoice.ecpay.com.tw/B2CInvoice/Issue'



def create_order(merchant_id, hash_key, hash_iv, order, return_url, order_result_url):
    item_name = ''
    for item in order.products:
        item_name += f'#{dict(order.products[item])["name"]}'
    params = {
    'MerchantTradeNo': str(order.id+datetime.now().strftime("%Y/%m/%d")) ,
    'StoreID': '',
    'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
    'PaymentType': 'aio',
    'TotalAmount': int(order.total),
    'TradeDesc': 'test order',
    'ItemName': item_name[1:],
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
        final_order_params = ecpay_payment_sdk.create_order(params)

        # 產生 html 的 form 格式
        action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
        # action_url = 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5' # 正式環境
        html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)
        # return action_url,final_order_params
        return action_url,final_order_params
    except Exception as error:
        print('An exception happened: ' + str(error))
        
def check_mac_value(merchant_id,hash_key,hash_iv,payment_res):
    
    ecpay_payment_sdk = ECPayPaymentSdk(
        MerchantID=merchant_id,
        HashKey=hash_key,
        HashIV=hash_iv
    )
    
    check_value = ecpay_payment_sdk.generate_check_value(payment_res)
    
    return check_value


def create_invoice(merchant_id,hash_key,hash_iv,order):
    ecpay_invoice = EcpayInvoice()
    
    ecpay_invoice.Invoice_Method = 'INVOICE'
    ecpay_invoice.Invoice_Url = Invoice_Url
    ecpay_invoice.MerchantID = merchant_id
    ecpay_invoice.HashKey = hash_key
    ecpay_invoice.HashIV = hash_iv
    
    ecpay_invoice.Send['Items'].append({
        'ItemName': '商品名稱一',
        'ItemCount': 1,
        'ItemWord': '批',
        'ItemPrice': int(order.total),
        'ItemTaxType': '',
        'ItemAmount': int(order.total),
        'ItemRemark': '商品備註一'
    })
    
    RelateNumber = 'ECPAY' + time.strftime("%Y%m%d%H%M%S", time.localtime())  # 產生測試用自訂訂單編號
    ecpay_invoice.Send['RelateNumber'] = RelateNumber
    ecpay_invoice.Send['CustomerID'] = ''
    ecpay_invoice.Send['CustomerIdentifier'] = ''
    ecpay_invoice.Send['CustomerName'] = order.shipping_last_name+order.shipping_first_name
    ecpay_invoice.Send['CustomerAddr'] = 'test   zzz'
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
    ecpay_invoice.Send['SalesAmount'] = int(order.total)
    ecpay_invoice.Send['InvoiceRemark'] = 'SDK TEST Python V1.0.6'
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
