from xml.etree.ElementTree import tostring
from backend.i18n._helper import lang_translate_default_en
from django.conf import settings
from django.utils.translation import ugettext as _
from math import prod,floor

@lang_translate_default_en
def i18n_get_mail_subject(order, lang=None):
    return _(
        'EMAIL/ORDER_CONFIRM/SUBJECT{order_id}{campaign_title}'
    ).format(order_id=order.id, campaign_title=order.campaign.title)


@lang_translate_default_en
def i18n_get_mail_content(order, campaign, lang=None):
    price_unit={
        "1":"",
        "1000":"K",
        "1000000":"M"
    }
    date_time = order.created_at.strftime("%b %d %Y")
    
    if 'code' not in order.applied_discount:
        discount_code = ''
    else:
        discount_code = str(order.applied_discount['code'])

    mail_content = f'<div style="width:100%; background: #eaeaea; font-family: \'Open Sans\', sans-serif;"><div style="margin: auto; padding:1%; max-width:900px; background: #ffffff;">'
    mail_content += f'<h1 data-key="1468266_heading" style="text-align:center; font-family: Georgia,serif,\'Playfair Display\'; font-size: 28px; line-height: 46px; font-weight: 700; color: #4b4b4b; text-transform: none; background-color: #ffffff; margin: 0;">' + _('EMAIL/ORDER_CONFIRM/TITLE') + '</h1>'
    mail_content += '<p data-key="1468270_order_number" style="text-align:center; color:#666363; font-weight: 500;">' + _('EMAIL/DELIVERY_CONFIRM/ORDER_NO') + f'# {str(order.id)} </p>'
    # mail_content = f'<h3>Order # {str(order.id)}</h3>'

    mail_content += '<div style="margin-top: 1%; font-size: 0.9rem; line-height: 2; sm:padding: 13px 30px;">\
                <p style="text-align: left; font-weight: 700; font-size: 1rem; line-height: 2;">' + _('EMAIL/DELIVERY_CONFIRM/ORDER_INFO') + '</p>\
                    <div style="border-bottom: 3px solid #ffd000; width: 20%; margin-bottom: 3%;"></div>'
    
    mail_content += '<table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%;" role="presentation">\
                        <tbody>\
                        <tr>\
                            <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/CAMPAIGN_TITLE') + f' : {order.campaign.title} </td>\
                        </tr>\
                        <tr>\
                            <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/ORDER_DATE') + f' : {date_time} </td>\
                        </tr>'
    try:
        if order.customer_name not in [None, '', "undefined", 'null']:
            mail_content+= '<tr>\
                                <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/BUYER') + f' : {order.customer_name}</td>\
                            </tr>'
    except:
        pass
    mail_content+=      '<tr>\
                            <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/RECEIVER') + f' : {order.shipping_first_name} {order.shipping_last_name}</td>\
                        </tr>\
                        <tr>\
                            <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('REPORT/COLUMN_TITLE/SHIPPING_PHONE') + f' : {order.shipping_phone}</td>\
                        </tr>'
    try:
        if order.shipping_method == 'pickup':
            mail_content+= f'<tr>\
                                <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('REPORT/COLUMN_TITLE/PICK_UP_STORE') + f' : {order.shipping_option} ,  {order.pickup_address}</td>\
                            </tr>'
                            # mail_content+= f'<b>Pick up date : </b>{meta["pick_up_date"]}<br><br>'
        else:
            mail_content+= f'<tr>\
                                <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/DELIVERY_ADDRESS') + f' : {order.shipping_address_1}, {order.shipping_location}, {order.shipping_region}, {order.shipping_postcode}</td>\
                            </tr>'
                            # mail_content+= f'<b>Delivery date : </b>{order_data["shipping_date"].strftime("%m/%d/%Y")}<br><br>'
    except:
        pass

    payment_method = ''
    if order.payment_method == 'direct_payment':
        payment_method = _('EMAIL/ORDER_CONFIRM/DIRECT_PAYMENT')
    else:
        payment_method = order.payment_method.upper()

    #payment
    mail_content += '<div style="margin-top: 1%; font-size: 0.9rem; line-height: 2; sm:padding: 13px 30px;">\
                <p style="text-align: left; font-weight: 700; font-size: 1rem; line-height: 2;">' + _('REPORT/SECTION_TITLE/PAYMENT_INFO') + '</p>\
                    <div style="border-bottom: 3px solid #ffd000; width: 20%; margin-bottom: 3%;"></div>'

    mail_content+=  f'<tr>\
                        <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('REPORT/COLUMN_TITLE/PAYMENT_METHOD') + f' : {payment_method}</td>\
                    </tr>\
                    <tr>\
                        <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/ORDER_CONFIRM/ACCOUNT_MODE') + f' : {order.meta["account_mode"]} </td>\
                    </tr>\
                    <tr>\
                        <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/ORDER_CONFIRM/SELLER_ACCOUNT') + f' : {order.meta["account_name"]} </td>\
                    </tr>'
    try:
        if order.meta["last_five_digit"] not in [None, '', "undefined", 'null']:
            mail_content+= f'<tr>\
                                <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/ORDER_CONFIRM/LAST_FIVE_DIGIT') + f' : {order.meta["last_five_digit"]}</td>\
                            </tr>'
        if order.meta["receipt_image"] not in [None, '', "undefined", 'null']:
            mail_content+=  f'<tr>\
                                <td style="color: #4b4b4b; font-weight: 600; text-align:left;" valign="top">\
                                    <img width="200" src="{order.meta["receipt_image"]}" alt="Product Image" style="vertical-align: middle; text-align: center; width: 200px; max-width: 200px; height: auto !important; border-radius: 1px; padding: 0px;">\
                                </td>\
                            </tr>'
    except:
        pass
    #contact
    mail_content += '<div style="margin-top: 1%; font-size: 0.9rem; line-height: 2; sm:padding: 13px 30px;">\
            <p style="text-align: left; font-weight: 700; font-size: 1rem; line-height: 2;">' + _('EMAIL/ORDER_CONFIRM/SELLER_CONTACT') + '</p>\
                <div style="border-bottom: 3px solid #ffd000; width: 20%; margin-bottom: 3%;"></div>'
    try:
        if campaign.facebook_page.page_id not in [None, '', "undefined", 'null']:
            mail_content+= f'<tr>\
                                <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">\
                                <a href="https://www.facebook.com/{campaign.facebook_page.page_id}"><div style="vertical-align: middle; width:auto; margin:auto; display: flex; flex-direction:row; align-items: center;">\
                                    <img style="width:30px; height:30px;" src="https://storage.googleapis.com/lss_public_bucket/static/email/facebook_icon.png" />\
                                    <p>Facebook : {campaign.facebook_page.name} </p>\
                                    </div></a>\
                                </td>\
                            </tr>'
        if campaign.instagram_profile.user_name not in [None, '', "undefined", 'null']:
            mail_content+= f'<tr>\
                                <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">\
                                <a href="https://www.instagram.com/{campaign.instagram_profile.user_name}"><div style="vertical-align: middle; width:auto; margin:auto; display: flex; flex-direction:row; align-items: center;">\
                                    <img style="width:30px; height:30px;" src="https://storage.googleapis.com/lss_public_bucket/static/email/instagram_icon.png" />\
                                    <p>Instagram : {campaign.instagram_profile.name} </p>\
                                    </div></a>\
                                </td>\
                            </tr>'
        if campaign.youtube_channel.channel_id not in [None, '', "undefined", 'null']:
            mail_content+= f'<tr>\
                                <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">\
                                <a href="https://www.youtube.com/channel/{campaign.youtube_channel.channel_id}"><div style="vertical-align: middle; width:auto; margin:auto; display: flex; flex-direction:row; align-items: center;">\
                                    <img style="width:30px; height:30px;" src="https://storage.googleapis.com/lss_public_bucket/static/email/youtube_icon.png" />\
                                    <p>Youtube : {campaign.youtube_channel.name} </p>\
                                    </div></a>\
                                </td>\
                            </tr>'
    except:
        pass
    mail_content +=     '</tbody>\
                    </table>'
    # mail_content+= f'<h3>{order.campaign.title}</h3>----------------------------------------<br>'
    # mail_content+= f'<b>Customer Name : </b>{order.customer_name}<br>'
    # mail_content+= f'<b>Delivery To : </b><br>' 
    # mail_content+= f'{order.shipping_first_name} {order.shipping_last_name}<br>'
    # mail_content+= f'{order.shipping_phone}<br>'
    # mail_content+= f'<b>Delivery way : </b>{order.shipping_method}<br>'

    mail_content += f'<table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%;" role="presentation"><tbody>'
    for key, product in order.products.items():
        mail_content += f'<tr>'
        mail_content += f'<td width="1" style="mso-line-height-rule: exactly; padding: 13px 13px 13px 0;" bgcolor="#ffffff" valign="middle">\
                            <img width="140" src="{product["image"]}" alt="Product Image" style="vertical-align: middle; text-align: center; width: 140px; max-width: 140px; height: auto !important; border-radius: 1px; padding: 0px;">\
                        </td>'
        mail_content += f'<tr style="mso-line-height-rule: exactly; padding-top: 13px; padding-bottom: 13px; border-bottom-width: 2px; border-bottom-color: #dadada; border-bottom-style: solid;" bgcolor="#ffffff" valign="middle">'
        mail_content += f'<table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%; border-bottom: 1px solid #a5a5a5;" role="presentation">\
                        <tbody>\
                            <tr>\
                            <td style="font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; padding: 13px 6px 13px 0;" align="left" bgcolor="#ffffff" valign="top">\
                                <p style="font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; margin: 0;" align="left">\
                                <a target="_blank" style="color: #666363; text-decoration: none !important; text-underline: none; word-wrap: break-word; text-align: left !important; font-weight: bold;">\
                                    {product["name"]}\
                                </a></p></td>'
        mail_content += f'<td style="bgcolor="#ffffff" valign="top"></td>\
                        <td width="1" style="white-space: nowrap; padding: 13px 0 13px 13px;" align="right" bgcolor="#ffffff" valign="top">\
                            <p style="font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; margin: 0;" align="right">\
                            x &nbsp;{product["qty"]}\
                            </p>\
                        </td>'
        mail_content += f'<td width="1" style="white-space: nowrap; padding: 13px 0 13px 26px;" align="right" bgcolor="#ffffff" valign="top">\
                                <p style="font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; margin: 0;" align="right">\
                                {order.campaign.currency}\
                                {adjust_decimal_places(product["subtotal"],order.campaign.decimal_places)}\
                                {price_unit[order.campaign.price_unit]}\
                                </p></td></tr></tbody></table></tr>'
        mail_content += f'</tr>'
    mail_content += f'</tbody></table>'
    
    # for key, product in order.products.items():
    #     mail_content+= f'<tr><td style="border: 1px solid black;">{product["name"]}</td><td style="border: 1px solid black;">${product["price"]}</td><td style="border: 1px solid black;">{product["qty"]}</td><td style="border: 1px solid black;">{product["subtotal"]}</td></tr>'
    # mail_content+= '</table>'

    mail_content += f'<table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%;" role="presentation">\
                        <tbody>\
                        <tr>\
                            <td data-key="1468271_subtotal" style="font-size: 15px; padding-top:13px; color: #4b4b4b; font-weight: 600; width: 35%; text-align:right;" align="right" bgcolor="#ffffff" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/SUBTOTAL') + f'\
                            <span style="width:120px; display:inline-block;">{order.campaign.currency}\
                            {adjust_decimal_places(order.subtotal,order.campaign.decimal_places)}\
                            {price_unit[order.campaign.price_unit]}</span></td>\
                        </tr>\
                        <tr>\
                            <td style="font-size: 15px; color: #4b4b4b; font-weight: 600; width: 35%; text-align:right; padding-bottom: 13px;" align="right" bgcolor="#ffffff" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/DISCOUNT') + f'<span style="color: #b91c1c;"> { discount_code } </span> \
                            <span style="width:120px; display:inline-block;">{order.campaign.currency}\
                            -{adjust_decimal_places(order.discount,order.campaign.decimal_places)}\
                            {price_unit[order.campaign.price_unit]}</span></td>\
                        </tr>\
                        <tr>\
                            <td style="font-size: 15px; color: #4b4b4b; font-weight: 600; width: 35%; text-align:right; padding-bottom: 13px;" align="right" bgcolor="#ffffff" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/DELIVERY_CHARGE') + f'\
                            <span style="width:120px; display:inline-block;">{order.campaign.currency}\
                            {adjust_decimal_places(order.shipping_cost,order.campaign.decimal_places)}\
                            {price_unit[order.campaign.price_unit]}</span></td>\
                        </tr>\
                        <tr>\
                            <td data-key="1468271_total" style="font-size: 15px; line-height: 26px; font-weight: bold; text-align:right; color: #666363; width: 65%; padding: 4px 0; border-top: 1px solid #666363;" align="left" bgcolor="#ffffff"  valign="top">' + _('EMAIL/DELIVERY_CONFIRM/TOTAL') + f'\
                            <span style="width:120px; display:inline-block;">{order.campaign.currency}\
                            {adjust_decimal_places(order.total,order.campaign.decimal_places)}\
                            {price_unit[order.campaign.price_unit]}</span></td>\
                        </tr>\
                        </tbody>\
                    </table>'
    # mail_content+= '<br>Delivery Charge: ' 
    # mail_content+= '$'+ str("%.2f" % float(order.shipping_cost))+'<br>'
    # mail_content+= 'Total : $' + str("%.2f" % float(order.total))

    mail_content += '<div style="background-color: #f5f5f5; max-width: 100%; padding: 13px 52px; font-size: 0.8rem; margin-top: 5%; text-align: center;">\
                <p>(*)' + _('EMAIL/DELIVERY_CONFIRM/DO_NOT_REPLY_1') + '</p>\
                <p>' + _('EMAIL/DELIVERY_CONFIRM/DO_NOT_REPLY_2') + '</p></div></div></div></div>'

    return mail_content 
    # mail_content = '<h3>' +_('EMAIL/ORDER_CONFIRM/ORDER') + f' # {str(order.id)}</h3>'
    # mail_content+= f'<h3>{order.campaign.title}</h3>----------------------------------------<br>'
    # mail_content+= '<b>' + _('EMAIL/ORDER_CONFIRM/CUSTOMER_NAME') + f' : </b>{order.customer_name}<br>'
    # mail_content+= '<b>' + _('EMAIL/ORDER_CONFIRM/DELIVERY_TO') + f' : </b><br>' 
    # mail_content+= f'{order.shipping_first_name} {order.shipping_last_name}<br>'
    # mail_content+= f'{order.shipping_phone}<br>'
    # mail_content+= '<b>' + _('EMAIL/ORDER_CONFIRM/DELIVERY_WAY') + f' : </b>{order.shipping_method}<br>'
    # try:
    #     if order.shipping_method == 'pickup':
    #         mail_content+= '<b>' + _('EMAIL/ORDER_CONFIRM/PICK_UP_STORE') + f' : </b>{order.shipping_option} ,  {order.pickup_address}<br>'
    #         # mail_content+= f'<b>Pick up date : </b>{meta["pick_up_date"]}<br><br>'
    #     else:
    #         mail_content+= '<b>' + _("EMAIL/ORDER_CONFIRM/DELIVERY_ADDRESS") + f' : </b>{order.shipping_address_1}, {order.shipping_location}, {order.shipping_region}, {order.shipping_postcode}<br>'
    #         # mail_content+= f'<b>Delivery date : </b>{order_data["shipping_date"].strftime("%m/%d/%Y")}<br><br>'
    # except:
    #     pass

    # mail_content+= '<b>' + _("EMAIL/ORDER_CONFIRM/PAYMENT_METHOD") + f' : </b>{order.payment_method}<br>'
    # mail_content+= '<table style="border-collapse: collapse;"><tr><th style="border: 1px solid black;">Item</th><th style="border: 1px solid black;">Price</th><th style="border: 1px solid black;">Qty</th><th style="border: 1px solid black;">Totoal</th></tr>'
    # for key, product in order.products.items():
    #     mail_content+= f'<tr><td style="border: 1px solid black;">{product["name"]}</td><td style="border: 1px solid black;">${product["price"]}</td><td style="border: 1px solid black;">{product["qty"]}</td><td style="border: 1px solid black;">{product["subtotal"]}</td></tr>'
    # mail_content+= '</table>'
    
    # mail_content+= '<br>' + _("EMAIL/ORDER_CONFIRM/DELIVERY_CHARGE") + ': ' 
    # mail_content+= f'${str("%.2f" % float(order.shipping_cost))}<br>'
    # mail_content+= _('EMAIL/ORDER_CONFIRM/TOTAL') + f' : ${str("%.2f" % float(order.total))}'

    # return mail_content
    
    
def adjust_decimal_places(num,decimal_places):
  if decimal_places == 0:
    return floor((num * (10 ** decimal_places))) // (10 ** decimal_places)
  else:
    return floor((num * (10 ** decimal_places))) / (10 ** decimal_places)
