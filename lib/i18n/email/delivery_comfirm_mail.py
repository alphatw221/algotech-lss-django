from itertools import product
from math import prod
from backend.i18n._helper import lang_translate_default_en
from django.conf import settings
from django.utils.translation import ugettext as _


@lang_translate_default_en
def i18n_get_mail_content(order, user, lang=None):
    date_time = order.created_at.strftime("%b %d %Y")
    shipping_date = order.updated_at.strftime("%b %d %Y")
    
    mail_content = f'<body style="background: #eaeaea; font-family: \'Open Sans\', sans-serif;"><main style="margin: 5% 30% 1% 30%;">'
    mail_content += f'<div style="background: #ffffff;"><div><div style=" padding: 13px 40px;"><div>\
                    <h1 data-key="1468266_heading" style="text-align:center; font-family: Georgia,serif,\'Playfair Display\'; font-size: 28px; line-height: 46px; font-weight: 700; color: #4b4b4b; text-transform: none; background-color: #ffffff; margin: 0;">Your Order Has Shipped</h1>'
    mail_content += f'<p data-key="1468270_order_number" style="text-align:center; color:#666363; font-weight: 500;">Order NO. #{order.id}</p></div>'
    
    mail_content += f'<div style="margin-top: 1%; font-size: 0.9rem; line-height: 2; sm:padding: 13px 40px;">\
                    <p style="text-align: left; font-weight: 700; font-size: 1rem; line-height: 2;">Order Information</p>\
                        <div style="border-bottom: 3px solid #ffd000; width: 20%; margin-bottom: 3%;"></div>'
    
    mail_content += f'<table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%;" role="presentation">\
                        <tbody>\
                          <tr>\
                            <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">Order Date</td>\
                            <td style="color: black; width: 65%; font-weight: 400; text-align: right;" valign="middle">{ date_time }</td>\
                          </tr>\
                          <tr>\
                            <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">Seller</td>\
                            <td style="color: black; width: 65%; font-weight: 400; text-align: right;" valign="middle">{ user.name }</td>\
                          </tr>\
                          <tr>\
                            <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">Seller\'s Email</td>\
                            <td style="color: black; width: 65%; font-weight: 400; text-align: right;" valign="middle">{ user.email }</td>\
                          </tr>\
                        </tbody>\
                      </table>'
    mail_content += f'</div>'
    
    
    mail_content += f'<table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%;" role="presentation"><tbody>'
    for key, product in order.products.items():
        mail_content += f'<tr>'
        mail_content += f'<td width="1" style="mso-line-height-rule: exactly; padding: 13px 13px 13px 0;" bgcolor="#ffffff" valign="middle">\
                            <img width="140" src="{settings.GS_URL+product["image"]}" alt="Product Image" style="vertical-align: middle; text-align: center; width: 140px; max-width: 140px; height: auto !important; border-radius: 1px; padding: 0px;">\
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
                              ×&nbsp;{product["qty"]}\
                            </p>\
                          </td>'
        mail_content += f'<td width="1" style="white-space: nowrap; padding: 13px 0 13px 26px;" align="right" bgcolor="#ffffff" valign="top">\
                                <p style="font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; margin: 0;" align="right">\
                                ${product["subtotal"]}\
                                </p></td></tr></tbody></table></tr>'
        mail_content += f'</tr>'
        
    mail_content += f'</tbody></table>'
    
    mail_content += f'<table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%;" role="presentation">\
                        <tbody>\
                          <tr>\
                            <td data-key="1468271_subtotal" style="padding-top:13px; color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" align="right" bgcolor="#ffffff" valign="top">Subtotal</td>\
                            <td style="padding-top:13px; color: black; width: 65%; font-weight: 400; text-align: right;" align="right" bgcolor="#ffffff"  valign="middle">${order.subtotal}</td>\
                          </tr>\
                          <tr>\
                            <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" align="right" bgcolor="#ffffff" valign="top">Delivery Charge</td>\
                            <td style="color: black; width: 65%; font-weight: 400; text-align: right;" align="right" bgcolor="#ffffff" valign="middle">${order.shipping_cost}</td>\
                          </tr>\
                          <tr>\
                            <td data-key="1468271_total" style="font-size: 15px; line-height: 26px; font-weight: bold; color: #666363; width: 65%; padding: 4px 0;" align="left" bgcolor="#ffffff"  valign="top">Total</td>\
                            <td style="color: black; width: 65%; font-weight: 400; text-align: right;" align="right" bgcolor="#ffffff" valign="middle">${order.total}</td>\
                          </tr>\
                        </tbody>\
                      </table>'
                  
    mail_content += f'<div style="margin-top: 1%; font-size: 0.9rem; line-height: 2;">\
                    <p style="text-align: left; font-weight: 700; font-size: 1rem; line-height: 2;">Shipping Information</p>\
                    <div style="border-bottom: 3px solid #ffd000; width: 20%; margin-bottom: 3%;"></div>\
                    <table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%;" role="presentation">\
                      <tbody>\
                        <tr>\
                          <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">Shipping Date</td>\
                          <td style="color: black; width: 65%; font-weight: 400; text-align: right;" valign="middle">{shipping_date}</td>\
                        </tr>\
                        <tr>\
                          <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">Delivery Address</td>\
                          <td style="color: black; width: 65%; font-weight: 400; text-align: right;" valign="middle">{order.shipping_location},{order.shipping_region},{order.shipping_postcode},{order.shipping_address_1}</td>\
                        </tr>\
                        <tr>\
                          <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">Remark</td>\
                          <td style="color: black; width: 65%; font-weight: 400; text-align: right;" valign="middle">{order.shipping_remark}</td>\
                        </tr>\
                      </tbody>\
                    </table>\
                  </div></div>'              
                  
    mail_content += f'<div style="background-color: #f5f5f5; max-width: 100%; padding: 13px 52px; font-size: 0.8rem; margin-top: 5%; text-align: center;">\
                  <p>(*)Please do not reply to this e-mail. This mailbox is not monitored and you will not receive a response.</p>\
                  <p>For questions about an order, other questions or comments, please contact Seller\'s email. You will be served faster than mail inquiry.</p></div></div></div>'
                  
    mail_content += f'</main></body>'

    return mail_content
