from backend.i18n._helper import lang_translate_default_en
from django.conf import settings
from django.utils.translation import ugettext as _


@lang_translate_default_en
def i18n_get_mail_content(order_id, campaign_data, order_data, lang=None):
    meta = order_data['meta']
    products = order_data['products']
    campaign_title = campaign_data['title']
    meta_logistic = campaign_data['meta_logistic']

    mail_content = 'Order # ' + str(order_id) + '\n\n'
    mail_content+= campaign_title + '\n--------------------------------------------\n'
    mail_content+= 'FB Name: ' + order_data['customer_name'] + '\n\n'
    mail_content+= 'Delivery To: \n' 
    mail_content+= order_data['shipping_first_name'] + ' ' + order_data['shipping_last_name'] + '\n\n'
    mail_content+= order_data['shipping_phone'] + '\n\n'
    
    try:
        if order_data['shipping_method'] == 'in_store':
            mail_content+= 'Shipping way: ' + order_data['shipping_method'] + '\n'
            mail_content+= 'Pick up store: ' + meta['pick_up_store'] + ', ' + meta['pick_up_store_address'] + '\n'
            mail_content+= 'Pick up date: ' + meta['pick_up_date'] + '\n'
        else:
            mail_content+= 'Shipping way: ' + order_data['shipping_method'] + '\n'
            mail_content+= 'Shipping address: ' + order_data['shipping_address_1'] + ', ' + order_data['shipping_location'] + ', ' + order_data['shipping_region'] + '\n'
            mail_content+= 'Shipping date: ' + order_data['shipping_date'].strftime('%m/%d/%Y') + '\n'
    except:
        pass

    mail_content+= '\n--------- Summary -----------\n'
    mail_content+= 'Price    Qty    Total      Item\n'
    mail_content+= '-----------------------------------\n'
    for key, val in products.items():
        mail_content+= '$' + str(products[key]['price']) + '  ' + str(products[key]['qty']).zfill(3) + '  $' + str(products[key]['subtotal']) + '    ' + products[key]['name'] + '\n'
    
    mail_content+= '\nDelivery Charge: ' 
    if order_data['free_delivery'] == False or order_data['shipping_method'] != 'in_store':
        mail_content+= '$' +  str("%.2f" % float(meta_logistic['delivery_charge'])) + '\n\n'
    else:
        mail_content+= '$0\n\n'
    mail_content+= 'Total          : $' + str("%.2f" % float(order_data['total']))

    return mail_content


@lang_translate_default_en
def i18n_get_mail_subject(shop_name, lang=None):
    mail_subject = '[LSS] '+ shop_name + ' order confirmation'
    return mail_subject