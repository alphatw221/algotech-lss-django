import os
from pyexpat import model
import config
import django
from math import prod,floor
from django.conf import settings


from api import models
from api_v2 import rule

import service
from ..error_handle.error_handler.pymongo_error_handler import pymongo_error_handler
import database
import traceback
from django.utils.translation import gettext as _


class RequestState():
    INIT = 'init'
    ADDING = 'adding'
    ADDED = 'added'
    UPDATING = 'updating'
    UPDATED = 'updated'
    DELETING = 'deleting'
    DELETED = 'deleted'
    INSUFFICIENT_INV = 'insufficient_inv'
    INVALID_PRODUCT_NOT_ACTIVATED = 'invalid_product_not_activated'
    INVALID_EXCEED_MAX_ORDER_AMOUNT = 'invalid_exceed_max_order_amount'
    INVALID_REMOVE_NOT_ALLOWED = 'invalid_remove_not_allowed'
    INVALID_EDIT_NOT_ALLOWED = 'invalid_edit_not_allowed'
    INVALID_NEGATIVE_QTY = 'invalid_negative_qty'
    INVALID_ADD_ZERO_QTY = 'invalid_add_zero_qty'
    INVALID_UNKNOWN_REQUEST = 'invalid_unknown_request'


class OrderHelper():


    @staticmethod
    def __caculate_subtotal(order):

        order.subtotal = 0
        for order_product in order.order_products.all():
            order.subtotal+=order_product.qty * order_product.price


    @classmethod
    def summarize_order(cls, order, save=True):

        #compute subtotal
        cls.__caculate_subtotal(order)

        campaign = order.campaign
        # #compute discount
        # lib.helper.discount_helper.make_discount_for_pre_order(pre_order)

        #compute shipping_cost
        if order.shipping_method == models.order.order.SHIPPING_METHOD_PICKUP:
            order.shipping_cost = 0
        else:
            order.shipping_cost = float(campaign.meta_logistic.get('delivery_charge',0))

            # delivery_options = meta_logistic.get('additional_delivery_options')

            if(type(order.shipping_option_index)==int):
                if order.shipping_option_data.get('type') == '+':
                    order.shipping_cost += float(order.shipping_option_data.get('price')) 

                elif order.shipping_option_data.get('type') == '=':
                    order.shipping_cost =  float(order.shipping_option_data.get('price'))

        #compute free_delivery
        meta_logistic = campaign.meta_logistic
        is_subtotal_over_free_delivery_threshold = order.subtotal >= float(meta_logistic.get('free_delivery_for_order_above_price')) if meta_logistic.get('is_free_delivery_for_order_above_price') else False
        is_items_over_free_delivery_threshold = len(order.products) >= float(meta_logistic.get('free_delivery_for_how_many_order_minimum')) if meta_logistic.get('is_free_delivery_for_how_many_order_minimum') else False
        order.meta['subtotal_over_free_delivery_threshold'] = True if is_subtotal_over_free_delivery_threshold else False
        order.meta['items_over_free_delivery_threshold'] = True if is_items_over_free_delivery_threshold else False
            

        #summarize_total
        total = 0
        total += order.subtotal
        total -= order.discount
        total = max(total, 0)
        if order.free_delivery or is_subtotal_over_free_delivery_threshold or is_items_over_free_delivery_threshold:
            pass
        else:
            total += order.shipping_cost
        total += order.adjust_price

        order.total = max(total, 0)

        if save:
            order.save()

        return order

    # @classmethod
    # @lang_translate_default_en
    # def get_confirmation_email_content(cls, order, lang=None):
    #     price_unit={
    #         "1":"",
    #         "1000":"K",
    #         "1000000":"M"
    #     }
    #     date_time = order.created_at.strftime("%b %d %Y")

    #     if 'code' not in order.applied_discount:
    #         discount_code = ''
    #     else:
    #         discount_code = str(order.applied_discount['code'])

    #     mail_content = f'<div style="width:100%; background: #eaeaea; font-family: \'Open Sans\', sans-serif;"><div style="margin: auto; padding:1%; max-width:900px; background: #ffffff;">'
    #     mail_content += f'<h1 data-key="1468266_heading" style="text-align:center; font-family: Georgia,serif,\'Playfair Display\'; font-size: 28px; line-height: 46px; font-weight: 700; color: #4b4b4b; text-transform: none; background-color: #ffffff; margin: 0;">Thanks for Ordering:</h1>'
    #     mail_content += '<p data-key="1468270_order_number" style="text-align:center; color:#666363; font-weight: 500;">' + _('ORDER_NO') + f'# {str(order.id)} </p>'
    #     # mail_content = f'<h3>Order # {str(order.id)}</h3>'

    #     mail_content += '<div style="margin-top: 1%; font-size: 0.9rem; line-height: 2; sm:padding: 13px 30px;">\
    #                 <p style="text-align: left; font-weight: 700; font-size: 1rem; line-height: 2;">' + _('EMAIL/DELIVERY_CONFIRM/ORDER_INFO') + '</p>\
    #                     <div style="border-bottom: 3px solid #ffd000; width: 20%; margin-bottom: 3%;"></div>'
        
    #     mail_content += '<table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%;" role="presentation">\
    #                         <tbody>\
    #                         <tr>\
    #                             <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/CAMPAIGN_TITLE') + f' : {order.campaign.title} </td>\
    #                         </tr>\
    #                         <tr style="height: 42px">\
    #                         </tr>\
    #                         <tr>\
    #                             <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/ORDER_DATE') + f' : {date_time} </td>\
    #                         </tr>'
    #     try:
    #         if order.customer_name not in ['undefined', '']:
    #             mail_content+= '<tr>\
    #                                 <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/BUYER') + f' : {order.customer_name}</td>\
    #                             </tr>'
    #     except:
    #         pass
    #     mail_content+=      '<tr>\
    #                             <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/RECEIVER') + f' : {order.shipping_first_name} {order.shipping_last_name}</td>\
    #                         </tr>\
    #                         <tr>\
    #                             <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('REPORT/COLUMN_TITLE/SHIPPING_PHONE') + f' : {order.shipping_phone}</td>\
    #                         </tr>\
    #                         <tr>'
    #     try:
    #         if order.shipping_method == 'pickup':
    #             mail_content+= f'<tr>\
    #                                 <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('REPORT/COLUMN_TITLE/PICK_UP_STORE') + f' : {order.shipping_option} ,  {order.pickup_address}</td>\
    #                             </tr>'
    #                             # mail_content+= f'<b>Pick up date : </b>{meta["pick_up_date"]}<br><br>'
    #         else:
    #             mail_content+= f'<tr>\
    #                                 <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/DELIVERY_ADDRESS') + f' : {order.shipping_address_1}, {order.shipping_location}, {order.shipping_region}, {order.shipping_postcode}</td>\
    #                             </tr>'
    #                             # mail_content+= f'<b>Delivery date : </b>{order_data["shipping_date"].strftime("%m/%d/%Y")}<br><br>'
    #     except:
    #         pass

    #     mail_content+= f'<tr>\
    #                         <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('REPORT/COLUMN_TITLE/PAYMENT_METHOD') + f' : {order.payment_method}</td>\
    #                     </tr>'

    #     mail_content +=     '</tbody>\
    #                     </table>'
    #     # mail_content+= f'<h3>{order.campaign.title}</h3>----------------------------------------<br>'
    #     # mail_content+= f'<b>Customer Name : </b>{order.customer_name}<br>'
    #     # mail_content+= f'<b>Delivery To : </b><br>' 
    #     # mail_content+= f'{order.shipping_first_name} {order.shipping_last_name}<br>'
    #     # mail_content+= f'{order.shipping_phone}<br>'
    #     # mail_content+= f'<b>Delivery way : </b>{order.shipping_method}<br>'

    #     mail_content += f'<table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%;" role="presentation"><tbody>'
    #     for key, product in order.products.items():
    #         mail_content += f'<tr>'
    #         mail_content += f'<td width="1" style="mso-line-height-rule: exactly; padding: 13px 13px 13px 0;" bgcolor="#ffffff" valign="middle">\
    #                             <img width="140" src="{product["image"]}" alt="Product Image" style="vertical-align: middle; text-align: center; width: 140px; max-width: 140px; height: auto !important; border-radius: 1px; padding: 0px;">\
    #                         </td>'
    #         mail_content += f'<tr style="mso-line-height-rule: exactly; padding-top: 13px; padding-bottom: 13px; border-bottom-width: 2px; border-bottom-color: #dadada; border-bottom-style: solid;" bgcolor="#ffffff" valign="middle">'
    #         mail_content += f'<table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%; border-bottom: 1px solid #a5a5a5;" role="presentation">\
    #                         <tbody>\
    #                             <tr>\
    #                             <td style="font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; padding: 13px 6px 13px 0;" align="left" bgcolor="#ffffff" valign="top">\
    #                                 <p style="font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; margin: 0;" align="left">\
    #                                 <a target="_blank" style="color: #666363; text-decoration: none !important; text-underline: none; word-wrap: break-word; text-align: left !important; font-weight: bold;">\
    #                                     {product["name"]}\
    #                                 </a></p></td>'
    #         mail_content += f'<td style="bgcolor="#ffffff" valign="top"></td>\
    #                         <td width="1" style="white-space: nowrap; padding: 13px 0 13px 13px;" align="right" bgcolor="#ffffff" valign="top">\
    #                             <p style="font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; margin: 0;" align="right">\
    #                             x &nbsp;{product["qty"]}\
    #                             </p>\
    #                         </td>'
    #         mail_content += f'<td width="1" style="white-space: nowrap; padding: 13px 0 13px 26px;" align="right" bgcolor="#ffffff" valign="top">\
    #                                 <p style="font-size: 16px; line-height: 26px; font-weight: 400; color: #666363; margin: 0;" align="right">\
    #                                 {order.campaign.currency}\
    #                                 {adjust_decimal_places(product["subtotal"],order.campaign.decimal_places)}\
    #                                 {price_unit[order.campaign.price_unit]}\
    #                                 </p></td></tr></tbody></table></tr>'
    #         mail_content += f'</tr>'
    #     mail_content += f'</tbody></table>'
    #     # for key, product in order.products.items():
    #     #     mail_content+= f'<tr><td style="border: 1px solid black;">{product["name"]}</td><td style="border: 1px solid black;">${product["price"]}</td><td style="border: 1px solid black;">{product["qty"]}</td><td style="border: 1px solid black;">{product["subtotal"]}</td></tr>'
    #     # mail_content+= '</table>'

    #     mail_content += f'<table cellspacing="0" cellpadding="0" border="0" width="100%" style="min-width: 100%;" role="presentation">\
    #                     <tbody>\
    #                     <tr>\
    #                         <td data-key="1468271_subtotal" style="font-size: 15px; padding-top:13px; color: #4b4b4b; font-weight: 600; width: 35%; text-align:right;" align="right" bgcolor="#ffffff" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/SUBTOTAL') + f'\
    #                         <span style="width:120px; display:inline-block;">{order.campaign.currency}\
    #                         {adjust_decimal_places(order.subtotal,order.campaign.decimal_places)}\
    #                         {price_unit[order.campaign.price_unit]}</span></td>\
    #                     </tr>\
    #                     <tr>\
    #                         <td style="font-size: 15px; color: #4b4b4b; font-weight: 600; width: 35%; text-align:right; padding-bottom: 13px;" align="right" bgcolor="#ffffff" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/DISCOUNT') + f'<span style="color: #b91c1c;"> { discount_code } </span> \
    #                         <span style="width:120px; display:inline-block;">{order.campaign.currency}\
    #                         -{adjust_decimal_places(order.discount,order.campaign.decimal_places)}\
    #                         {price_unit[order.campaign.price_unit]}</span></td>\
    #                     </tr>\
    #                     <tr>\
    #                         <td style="font-size: 15px; color: #4b4b4b; font-weight: 600; width: 35%; text-align:right; padding-bottom: 13px;" align="right" bgcolor="#ffffff" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/DELIVERY_CHARGE') + f'\
    #                         <span style="width:120px; display:inline-block;">{order.campaign.currency}\
    #                         {adjust_decimal_places(order.shipping_cost,order.campaign.decimal_places)}\
    #                         {price_unit[order.campaign.price_unit]}</span></td>\
    #                     </tr>\
    #                     <tr>\
    #                         <td data-key="1468271_total" style="font-size: 15px; line-height: 26px; font-weight: bold; text-align:right; color: #666363; width: 65%; padding: 4px 0; border-top: 1px solid #666363;" align="left" bgcolor="#ffffff"  valign="top">' + _('EMAIL/DELIVERY_CONFIRM/TOTAL') + f'\
    #                         <span style="width:120px; display:inline-block;">{order.campaign.currency}\
    #                         {adjust_decimal_places(order.total,order.campaign.decimal_places)}\
    #                         {price_unit[order.campaign.price_unit]}</span></td>\
    #                     </tr>\
    #                     </tbody>\
    #                 </table>'
        
    #     # mail_content+= '<br>Delivery Charge: ' 
    #     # mail_content+= '$'+ str("%.2f" % float(order.shipping_cost))+'<br>'
    #     # mail_content+= 'Total : $' + str("%.2f" % float(order.total))

    #     mail_content += '<div style="background-color: #f5f5f5; max-width: 100%; padding: 13px 52px; font-size: 0.8rem; margin-top: 5%; text-align: center;">\
    #               <p>(*)' + _('EMAIL/DELIVERY_CONFIRM/DO_NOT_REPLY_1') + '</p>\
    #               <p>' + _('EMAIL/DELIVERY_CONFIRM/DO_NOT_REPLY_2') + '</p></div></div></div></div>'

    #     return mail_content 


    
    @classmethod
    @pymongo_error_handler
    def sold_campaign_product(cls, order):

       for campaign_product_id_str, qty in order.products.items():
            pymongo_campaign_product = database.lss.campaign_product.CampaignProduct(id=int(campaign_product_id_str))
            pymongo_campaign_product.sold(qty, sync=True)
            campaign_product_data = pymongo_campaign_product.data
            
            product_data = {
                "id": campaign_product_data.get('id'),
                'qty_sold': campaign_product_data.get('qty_sold'),
                'qty_pending_payment':campaign_product_data.get('qty_pending_payment'),
                "qty_add_to_cart":campaign_product_data.get('qty_add_to_cart'),

            }

            service.channels.campaign.send_product_data(campaign_product_data.get("campaign_id"), product_data)
            
            
def adjust_decimal_places(num,decimal_places):
  if decimal_places == 0:
    return floor((num * (10 ** decimal_places))) // (10 ** decimal_places)
  else:
    return floor((num * (10 ** decimal_places))) / (10 ** decimal_places)





class OrderStatusHelper():

    payment_final_status=[models.order.order.PAYMENT_STATUS_PAID,models.order.order.PAYMENT_STATUS_REFUNDED]
    delivery_final_status=[models.order.order.DELIVERY_STATUS_COLLECTED,models.order.order.DELIVERY_STATUS_RETURNED]

    payment_status_graph={
        models.order.order.PAYMENT_STATUS_AWAITING_PAYMENT:[
            models.order.order.PAYMENT_STATUS_FAILED ,
            models.order.order.PAYMENT_STATUS_EXPIRED ,
            models.order.order.PAYMENT_STATUS_PAID ,
        ],
        models.order.order.PAYMENT_STATUS_FAILED:[
            models.order.order.PAYMENT_STATUS_AWAITING_PAYMENT ,
            models.order.order.PAYMENT_STATUS_EXPIRED ,
            models.order.order.PAYMENT_STATUS_PAID ,
        ],
        models.order.order.PAYMENT_STATUS_EXPIRED:[
            models.order.order.PAYMENT_STATUS_AWAITING_PAYMENT ,
            models.order.order.PAYMENT_STATUS_FAILED ,
        ],
        models.order.order.PAYMENT_STATUS_PAID:[
            models.order.order.PAYMENT_STATUS_AWAITING_REFUND ,
            models.order.order.PAYMENT_STATUS_REFUNDED ,
        ],
        models.order.order.PAYMENT_STATUS_AWAITING_REFUND:[
            models.order.order.PAYMENT_STATUS_REFUNDED ,
        ],
    }

    delivery_status_graph={
        models.order.order.DELIVERY_STATUS_AWAITING_FULFILLMENT:[
            models.order.order.DELIVERY_STATUS_AWAITING_SHIPMENT ,
            models.order.order.DELIVERY_STATUS_AWAITING_PICKUP ,
        ],
        models.order.order.DELIVERY_STATUS_AWAITING_SHIPMENT:[
            models.order.order.DELIVERY_STATUS_PARTIALLY_SHIPPED ,
            models.order.order.DELIVERY_STATUS_SHIPPED ,
        ],
        models.order.order.DELIVERY_STATUS_AWAITING_PICKUP:[
            models.order.order.DELIVERY_STATUS_COLLECTED ,
        ],
        models.order.order.DELIVERY_STATUS_PARTIALLY_SHIPPED:[
            models.order.order.DELIVERY_STATUS_SHIPPED ,
        ],
        models.order.order.DELIVERY_STATUS_SHIPPED:[
            models.order.order.DELIVERY_STATUS_COLLECTED ,
        ],
        models.order.order.DELIVERY_STATUS_COLLECTED:[
            models.order.order.DELIVERY_STATUS_AWAITING_RETURN ,
        ],
        models.order.order.DELIVERY_STATUS_AWAITING_RETURN:[
            models.order.order.DELIVERY_STATUS_RETURNED ,
        ],
    }

    @classmethod
    def update_order_status(cls, order:models.order.order.Order, save=False):
        if order.delivery_status in cls.delivery_final_status and order.payment_status in cls.payment_final_status:
            order.status = models.order.order.STATUS_COMPLETE
        else:
            order.status = models.order.order.STATUS_PROCEED
        
        if save:
            order.save()
