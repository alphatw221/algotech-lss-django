from itertools import product
from math import prod
from backend.i18n._helper import lang_translate_default_en
from django.conf import settings
from django.utils.translation import ugettext as _


@lang_translate_default_en
def i18n_get_mail_content(order, user, lang=None):
    date_time = order.created_at.strftime("%b %d %Y")
    shipping_date = order.updated_at.strftime("%b %d %Y")

    mail_content = f'<div style="margin: 5% 25% 1% 25%; background: #ffffff;"><div><div style="padding: 13px 52px;"><div>\
                    <h1 data-key="1468266_heading" style="text-align:center; font-family: Georgia,serif,\'Playfair Display\'; font-size: 28px; line-height: 46px; font-weight: 700; color: #4b4b4b; text-transform: none; background-color: #ffffff; margin: 0;">Your Order Has Shipped</h1>'
    mail_content += f'<p data-key="1468270_order_number" style="text-align:center; color:#666363; font-weight: 500;">Order NO. #{order.id}</p></div>'
    
    mail_content += f'<div style="margin-top: 1%; font-size: 0.9rem; line-height: 2;">\
                    <p style="text-align: left; font-weight: 700; font-size: 1rem; line-height: 2;">Order Information</p>\
                        <div style="border-bottom: 3px solid #ffd000; width: 5vw; margin-bottom: 3%;"></div>'
    mail_content += f'<span style="float: right;color: #4b4b4b; font-weight: 600;">Order Date : { date_time }</span>'
    mail_content += f'<div><span style="color: #4b4b4b; font-weight: 600;">Seller</span> : { user.name }</div>'
    mail_content += f'<div><span style="color: #4b4b4b; font-weight: 600;">Seller Email</span> : { user.email }</div></div>'
    
    mail_content += f'<tr>'
    for key, product in order.products.items():
        mail_content += f'<th width="1" style="mso-line-height-rule: exactly; border-bottom-width: 2px; border-bottom-color: #dadada; border-bottom-style: solid; padding: 13px 13px 13px 0;" bgcolor="#ffffff" valign="middle">\
                            <img width="140" class="product-image" src="{settings.GS_URL+product["image"]}" alt="Product Image" style="vertical-align: middle; text-align: center; width: 140px; max-width: 140px; height: auto !important; border-radius: 1px; padding: 0px;">\
                        </th>'
        mail_content += f'<th style="mso-line-height-rule: exactly; padding-top: 13px; padding-bottom: 13px; border-bottom-width: 2px; border-bottom-color: #dadada; border-bottom-style: solid;" bgcolor="#ffffff" valign="middle">'
        mail_content += f'<table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%; border-bottom: 1px solid #a5a5a5;" role="presentation">\
                          <tbody>\
                            <tr>\
                              <th style="mso-line-height-rule: exactly; font-family: -apple-system,BlinkMacSystemFont,\'Segoe UI\',Arial,\'Karla\'; font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; padding: 13px 6px 13px 0;" align="left" bgcolor="#ffffff" valign="top">\
                                <p style="mso-line-height-rule: exactly; font-family: -apple-system,BlinkMacSystemFont,\'Segoe UI\',Arial,\'Karla\'; font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; margin: 0;" align="left">\
                                <a target="_blank" style="color: #666363; text-decoration: none !important; text-underline: none; word-wrap: break-word; text-align: left !important; font-weight: bold;">\
                                    {product["name"]}\
                                </a><br></p></th>'
        mail_content += f'<th style="mso-line-height-rule: exactly;" bgcolor="#ffffff" valign="top"></th>\
                              <th width="1" style="mso-line-height-rule: exactly; white-space: nowrap; padding: 13px 0 13px 13px;" align="right" bgcolor="#ffffff" valign="top">\
                                <p style="mso-line-height-rule: exactly; font-family: -apple-system,BlinkMacSystemFont,\'Segoe UI\',Arial,\'Karla\'; font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; margin: 0;" align="right">\
                                ×&nbsp;{product["qty"]}\
                                </p></th>'
        mail_content += f'<th width="1" style="mso-line-height-rule: exactly; white-space: nowrap; padding: 13px 0 13px 26px;" align="right" bgcolor="#ffffff" valign="top">\
                                <p style="mso-line-height-rule: exactly; font-family: -apple-system,BlinkMacSystemFont,\'Segoe UI\',Arial,\'Karla\'; font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; margin: 0;" align="right">\
                                ${product["subtotal"]}\
                                </p></th></tr></tbody></table></th>'
    mail_content += f'</tr>'
    
    mail_content += f'<div style="margin-top: 1%; font-size: 0.9rem; line-height: 2;">\
                    <p style="text-align: left; font-weight: 700; font-size: 1rem; line-height: 2;">Shipping Information</p>\
                    <div style="border-bottom: 3px solid #ffd000; width: 5vw; margin-bottom: 3%;"></div>\
                    <div><span style="color: #4b4b4b; font-weight: 600;">Shipping Date</span> : {shipping_date}</div>\
                    <div><span style="color: #4b4b4b; font-weight: 600;">Delivery Address</span> : {order.shipping_location},{order.shipping_region},{order.shipping_postcode},{order.shipping_address_1}</div>\
                    <div><span style="color: #4b4b4b; font-weight: 600;">Remark</span> : {order.shipping_remark}</div>\
                  </div></div>'
    mail_content += f'<div style="background-color: #f5f5f5; max-width: 100%; padding: 13px 52px; font-size: 0.8rem; margin-top: 5%; text-align: center;">\
                  <p>(*)Please do not reply to this e-mail. This mailbox is not monitored and you will not receive a response.</p>\
                  <p>For questions about an order, other questions or comments, please contact Seller\'s email. You will be served faster than mail inquiry.</p></div></div></div>'

    return mail_content
