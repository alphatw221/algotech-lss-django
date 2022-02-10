from math import prod
from backend.i18n._helper import lang_translate_default_en
from django.conf import settings
from django.utils.translation import ugettext as _


@lang_translate_default_en
def i18n_get_mail_content(order_id, campaign_data, order_data, shop_name, lang=None):
    meta = order_data['meta']
    products = order_data['products']
    campaign_title = campaign_data['title']
    meta_logistic = campaign_data['meta_logistic']

    mail_content = f'<h3>Order # {str(order_id)}</h3>'
    mail_content+= f'<h3>{shop_name} : {campaign_title}</h3>----------------------------------------<br>'
    mail_content+= f'<b>FB Name : </b>{order_data["customer_name"]}<br>'
    mail_content+= f'<b>Delivery To : </b><br>' 
    mail_content+= f'{order_data["shipping_first_name"]} {order_data["shipping_last_name"]}<br>'
    mail_content+= f'{order_data["shipping_phone"]}<br>'
    mail_content+= f'<b>Delivery way : </b>{order_data["shipping_method"]}<br>'
    try:
        if order_data['shipping_method'] == 'in_store':
            mail_content+= f'<b>Pick up store : </b>{meta["pick_up_store"]} ,  {meta["pick_up_store_address"]}<br>'
            mail_content+= f'<b>Pick up date : </b>{meta["pick_up_date"]}<br><br>'
        else:
            mail_content+= f'<b>Delivery address : </b>{order_data["shipping_address_1"]}, {order_data["shipping_location"]}, {order_data["shipping_region"]}, {order_data["shipping_postcode"]}<br>'
            mail_content+= f'<b>Delivery date : </b>{order_data["shipping_date"].strftime("%m/%d/%Y")}<br><br>'
    except:
        pass
    # mail_content+= '\n----------- Summary -----------\n'
    # mail_content+= 'Price    Qty    Total      Item\n'
    # mail_content+= '-----------------------------\n'
    # for key, val in products.items():
    #     mail_content+= '$' + str(products[key]['price']) + '   ' + str(products[key]['qty']).zfill(3) + '   $' + str(products[key]['subtotal']) + '    ' + products[key]['name'] + '\n'

    mail_content+= f'<b>Payment method : </b>{order_data["payment_method"]}<br>'
    mail_content+= '<table style="border-collapse: collapse;"><tr><th style="border: 1px solid black;">Item</th><th style="border: 1px solid black;">Price</th><th style="border: 1px solid black;">Qty</th><th style="border: 1px solid black;">Totoal</th></tr>'
    for key, product in products.items():
        mail_content+= f'<tr><td style="border: 1px solid black;">{product["name"]}</td><td style="border: 1px solid black;">${product["price"]}</td><td style="border: 1px solid black;">{product["qty"]}</td><td style="border: 1px solid black;">{product["subtotal"]}</td></tr>'
    mail_content+= '</table>'
    
    mail_content+= '<br>Delivery Charge: ' 
    if order_data['shipping_method'] == 'in_store':
        mail_content+= '$0<br>'
    else:
        if order_data['free_delivery'] == False or order_data['shipping_method'] != 'in_store':
            mail_content+= '$' +  str("%.2f" % float(meta_logistic['delivery_charge'])) + '<br>'
        else:
            mail_content+= '$0<br>'
    mail_content+= 'Total : $' + str("%.2f" % float(order_data['total']))

    return mail_content


@lang_translate_default_en
def i18n_get_mail_subject(shop_name, lang=None):
    mail_subject = '[LSS] '+ shop_name + ' order confirmation'
    return mail_subject