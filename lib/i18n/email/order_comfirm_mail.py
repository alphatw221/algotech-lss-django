from backend.i18n._helper import lang_translate_default_en
from django.conf import settings
from django.utils.translation import ugettext as _


@lang_translate_default_en
def i18n_get_mail_subject(order):
    return _(
        'EMAIL/ORDER_CONFIRM/SUBJECT{order_id}{campaign_title}'
    ).format(order_id=order.id, campaign_title=order.campaign.title)


@lang_translate_default_en
def i18n_get_mail_content(order):
    mail_content = '<h3>' +_('EMAIL/ORDER_CONFIRM/ORDER') + f' # {str(order.id)}</h3>'
    mail_content+= f'<h3>{order.campaign.title}</h3>----------------------------------------<br>'
    mail_content+= '<b>' + _('EMAIL/ORDER_CONFIRM/CUSTOMER_NAME') + f' : </b>{order.customer_name}<br>'
    mail_content+= '<b>' + _('EMAIL/ORDER_CONFIRM/DELIVERY_TO') + f' : </b><br>' 
    mail_content+= f'{order.shipping_first_name} {order.shipping_last_name}<br>'
    mail_content+= f'{order.shipping_phone}<br>'
    mail_content+= '<b>' + _('EMAIL/ORDER_CONFIRM/DELIVERY_WAY') + f' : </b>{order.shipping_method}<br>'
    try:
        if order.shipping_method == 'pickup':
            mail_content+= '<b>' + _('EMAIL/ORDER_CONFIRM/PICK_UP_STORE') + f' : </b>{order.shipping_option} ,  {order.pickup_address}<br>'
            # mail_content+= f'<b>Pick up date : </b>{meta["pick_up_date"]}<br><br>'
        else:
            mail_content+= '<b>' + _("EMAIL/ORDER_CONFIRM/DELIVERY_ADDRESS") + f' : </b>{order.shipping_address_1}, {order.shipping_location}, {order.shipping_region}, {order.shipping_postcode}<br>'
            # mail_content+= f'<b>Delivery date : </b>{order_data["shipping_date"].strftime("%m/%d/%Y")}<br><br>'
    except:
        pass

    mail_content+= '<b>' + _("EMAIL/ORDER_CONFIRM/PAYMENT_METHOD") + f' : </b>{order.payment_method}<br>'
    mail_content+= '<table style="border-collapse: collapse;"><tr><th style="border: 1px solid black;">Item</th><th style="border: 1px solid black;">Price</th><th style="border: 1px solid black;">Qty</th><th style="border: 1px solid black;">Totoal</th></tr>'
    for key, product in order.products.items():
        mail_content+= f'<tr><td style="border: 1px solid black;">{product["name"]}</td><td style="border: 1px solid black;">${product["price"]}</td><td style="border: 1px solid black;">{product["qty"]}</td><td style="border: 1px solid black;">{product["subtotal"]}</td></tr>'
    mail_content+= '</table>'
    
    mail_content+= '<br>' + _("EMAIL/ORDER_CONFIRM/DELIVERY_CHARGE") + ': ' 
    mail_content+= f'${str("%.2f" % float(order.shipping_cost))}<br>'
    mail_content+= _('EMAIL/ORDER_CONFIRM/TOTAL') + f' : ${str("%.2f" % float(order.total))}'

    return mail_content
