import os
import config
import django
from math import prod,floor
from django.conf import settings


from api import rule,models

import service
import lib
import database
import traceback
from django.utils.translation import gettext as _
from datetime import datetime
from enum import Enum, auto
from backend.i18n._helper import lang_translate_default_en


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


class PreOrderHelper():


    @classmethod
    @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    def add_product(cls, api_user, pre_order_id, campaign_product_id, qty):

        with database.lss.util.start_session() as session:
            with session.start_transaction():
                pre_order = database.lss.pre_order.PreOrder.get_object(id=pre_order_id,session=session)
                campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=campaign_product_id,session=session)

                ret = rule.rule_checker.pre_order_rule_checker.RuleChecker.check(
                    check_list=[
                        rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_campaign_product_exist,
                        rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_order_lock,
                        rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_qty_valid,
                        rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_order_product_addable,
                        rule.check_rule.pre_order_check_rule.PreOrderCheckRule.campaign_product_type,
                        rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_stock_avaliable,
                        rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_under_max_limit,
                    ],
                    **{
                        'api_user':api_user,
                        'api_pre_order':pre_order.data,
                        'api_campaign_product':campaign_product.data,
                        'qty':qty,
                    })

                qty = ret.get('qty')
                qty_difference = ret.get('qty_difference')
                
                cls._add_product(api_user, pre_order, campaign_product, qty, qty_difference, session=session)
        return pre_order

    @classmethod
    def add_product_by_comment(cls, pre_order_id, campaign_product_id, qty):
        with database.lss.util.start_session() as session:
            with session.start_transaction():

                pre_order = database.lss.pre_order.PreOrder.get_object(id=pre_order_id,session=session)
                campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=campaign_product_id,session=session)

                ret = rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_stock_avaliable(**{'api_campaign_product':campaign_product.data,'qty':qty})
                qty_difference = ret.get('qty_difference')

                cls._add_product(None, pre_order, campaign_product, qty, qty_difference ,session=session)


    @staticmethod
    def _add_product(api_user, pre_order, campaign_product, qty, qty_difference, session):
        order_product = database.lss.order_product.OrderProduct.create_object(
            campaign_id= campaign_product.data.get('campaign_id'),
            campaign_product_id= campaign_product.id,
            pre_order_id=pre_order.id,
            qty= qty,
            customer_id=pre_order.data.get('customer_id'),
            customer_name= pre_order.data.get('customer_name'),
            platform=pre_order.data.get('platform'),
            type=campaign_product.data.get("type"),
            name=campaign_product.data.get("name"),
            price=campaign_product.data.get("price"),
            image=campaign_product.data.get("image"),
            subtotal=float(qty*campaign_product.data.get("price")),
            session=session)

        order_product_data = {
            "order_product_id": order_product.id,
            "name": campaign_product.data.get("name"),
            "image": campaign_product.data.get("image"),
            "price": campaign_product.data.get("price"),
            "type": campaign_product.data.get("type"),
            "qty": qty,
            "subtotal": float(qty*campaign_product.data.get("price"))
        }

        subtotal = pre_order.data.get('subtotal')+(qty_difference*campaign_product.data.get('price'))
        free_delivery = pre_order.data.get("free_delivery",False)
        shipping_cost = 0 if free_delivery else pre_order.data.get('shipping_cost',0)
        adjust_price = pre_order.data.get("adjust_price",0)
        total = subtotal+ float(shipping_cost)+float(adjust_price)
        total = 0 if total<0 else total

        data ={
            "lock_at": datetime.now() if api_user and api_user.type == 'customer' else None,
            f"products.{str(campaign_product.id)}": order_product_data,
            "subtotal":subtotal,
            "total":total
        }

        pre_order.update(**data, session=session, sync=True)
        campaign_product.add_to_cart(qty_difference, session=session)
        
        product_data = {
            "id": campaign_product.id,
            'qty_sold': campaign_product.data.get('qty_sold'),
            'qty_pending_payment':campaign_product.data.get('qty_pending_payment'),
            "qty_add_to_cart":campaign_product.data.get('qty_add_to_cart'),

        }
        service.channels.campaign.send_order_data(campaign_product.data.get("campaign_id"), pre_order.data)
        service.channels.campaign.send_product_data(campaign_product.data.get("campaign_id"), product_data)



    @classmethod
    @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    def update_product(cls, api_user, pre_order_id, order_product_id, qty):

        with database.lss.util.start_session() as session:
            with session.start_transaction():

                pre_order = database.lss.pre_order.PreOrder.get_object(id=pre_order_id,session=session)
                order_product = database.lss.order_product.OrderProduct.get_object(id=order_product_id,session=session)
                campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=order_product.data.get('campaign_product_id'),session=session)

                ret = rule.rule_checker.pre_order_rule_checker.RuleChecker.check(check_list=[
                    rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_campaign_product_exist,
                    rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_order_lock,
                    rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_qty_valid,
                    rule.check_rule.pre_order_check_rule.PreOrderCheckRule.campaign_product_type,
                    rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_order_product_editable,
                    rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_stock_avaliable,
                    rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_under_max_limit,
                    ],**{
                    'api_user':api_user,
                    'api_pre_order':pre_order.data,
                    'api_order_product':order_product.data,
                    'api_campaign_product':campaign_product.data,
                    'qty':qty,
                    })

                qty = ret.get('qty')
                qty_difference = ret.get('qty_difference')
                
                cls._update_product(pre_order, order_product, campaign_product, qty, qty_difference, api_user, session)
        return pre_order

    @classmethod
    def update_product_by_comment(cls, pre_order_id, campaign_product_id, qty):

        with database.lss.util.start_session() as session:
            with session.start_transaction():

                pre_order = database.lss.pre_order.PreOrder.get_object(id=pre_order_id,session=session)
                campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=campaign_product_id,session=session)
                order_product = database.lss.order_product.OrderProduct.get_object(pre_order_id=pre_order_id,campaign_product_id=campaign_product_id,session=session)
                
                ret = rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_stock_avaliable(**{'api_campaign_product':campaign_product.data,'qty':qty,'api_order_product':order_product.data})
                qty_difference = ret.get('qty_difference')

                cls._update_product(pre_order, order_product, campaign_product, qty, qty_difference, None, session=session)
                
                campaign_product._sync(session=session)
                

    @staticmethod
    def _update_product(pre_order, order_product, campaign_product, qty, qty_difference, api_user, session):
        
        order_product.update(qty=qty, subtotal=float(qty*campaign_product.data.get("price")), session=session)

        subtotal = pre_order.data.get('subtotal')+qty_difference*campaign_product.data.get('price')
        free_delivery = pre_order.data.get("free_delivery",False)
        shipping_cost = 0 if free_delivery else pre_order.data.get('shipping_cost',0)
        adjust_price = pre_order.data.get("adjust_price",0)
        total = subtotal+ float(shipping_cost)+float(adjust_price)
        total = 0 if total<0 else total
        

        data ={
            "lock_at": datetime.now() if api_user and api_user.type == 'customer' else None,
            f"products.{str(campaign_product.id)}.{'qty'}": qty,
            f"products.{str(campaign_product.id)}.{'subtotal'}": float(qty*order_product.data.get('price')),
            "subtotal":subtotal,
            "total":total
        }
        campaign_product.add_to_cart(qty_difference, session=session)
        pre_order.update(**data, session=session, sync=True)

        product_data = {
            "id": campaign_product.id,
            'qty_sold': campaign_product.data.get('qty_sold'),
            'qty_pending_payment':campaign_product.data.get('qty_pending_payment'),
            "qty_add_to_cart":campaign_product.data.get('qty_add_to_cart'),

        }
        service.channels.campaign.send_order_data(campaign_product.data.get("campaign_id"), pre_order.data)
        service.channels.campaign.send_product_data(campaign_product.data.get("campaign_id"), product_data)


    @classmethod
    @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    def delete_product(cls, api_user, pre_order_id, order_product_id):

        with database.lss.util.start_session() as session:
            with session.start_transaction():

                pre_order = database.lss.pre_order.PreOrder.get_object(id=pre_order_id,session=session)
                order_product = database.lss.order_product.OrderProduct.get_object(id=order_product_id,session=session)
                campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=order_product.data.get('campaign_product_id'),session=session)

                rule.rule_checker.pre_order_rule_checker.RuleChecker.check(
                    check_list=[
                        rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_order_lock,
                        rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_order_product_removeable
                    ],**{
                    'api_user':api_user,
                    'api_pre_order':pre_order.data,
                    'api_order_product':order_product.data,
                    'api_campaign_product':campaign_product.data,
                    })
                cls._delete_product(pre_order, campaign_product, order_product, api_user, session)
        return True

    @classmethod
    def delete_product_by_comment(cls, pre_order_id, campaign_product_id):
        with database.lss.util.start_session() as session:
            with session.start_transaction():

                pre_order = database.lss.pre_order.PreOrder.get_object(id=pre_order_id, session=session)
                campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=campaign_product_id, session=session)
                order_product = database.lss.order_product.OrderProduct.get_object(pre_order_id=pre_order_id, campaign_product_id=campaign_product_id, session=session)

                cls._delete_product(pre_order, campaign_product, order_product, None, session)
                
              

    @staticmethod
    def _delete_product(pre_order, campaign_product, order_product, api_user, session):
        
        subtotal = pre_order.data.get('subtotal')-order_product.data.get('qty')*order_product.data.get('price')
        free_delivery = pre_order.data.get("free_delivery",False)
        shipping_cost = 0 if free_delivery else pre_order.data.get('shipping_cost',0)
        adjust_price = pre_order.data.get("adjust_price",0)
        total = subtotal+ float(shipping_cost)+float(adjust_price)
        total = 0 if total<0 else total

        data = {
                    "lock_at": datetime.now() if api_user and api_user.type == 'customer' else None,
                    "subtotal":subtotal,
                    "total":total
                }
        campaign_product.customer_return(order_product.data.get('qty'), session=session)
        pre_order.delete_product(campaign_product, session=session, sync=True, **data)
        order_product.delete(session=session)

        product_data = {
            "id": campaign_product.id,
            'qty_sold': campaign_product.data.get('qty_sold'),
            'qty_pending_payment':campaign_product.data.get('qty_pending_payment'),
            "qty_add_to_cart":campaign_product.data.get('qty_add_to_cart'),
        }

        service.channels.campaign.send_order_data(campaign_product.data.get("campaign_id"), pre_order.data)
        service.channels.campaign.send_product_data(campaign_product.data.get("campaign_id"), product_data)


    @classmethod
    @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    def checkout(cls, api_user, campaign_id, pre_order_id):

        with database.lss.util.start_session() as session:
            with session.start_transaction():

                success = True
                campaign = database.lss.campaign.Campaign.get_object(id=campaign_id,session=session)
                pre_order = database.lss.pre_order.PreOrder.get_object(id=pre_order_id,session=session)

                rule.rule_checker.pre_order_rule_checker.RuleChecker.check(
                    check_list=[
                        rule.check_rule.pre_order_check_rule.PreOrderCheckRule.allow_checkout,
                        rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_order_lock,
                        rule.check_rule.pre_order_check_rule.PreOrderCheckRule.is_order_empty
                    ],**{
                        'api_user':api_user,
                        'api_pre_order':pre_order.data,
                        'campaign':campaign
                    })

                campaign_product_qty_tuples = []
                for campaign_product_id_str, order_product_info in pre_order.data.get('products',{}).items():            
                    order_product_data = pre_order.data.get('products',{}).get(campaign_product_id_str)
                    order_product = database.lss.order_product.OrderProduct.get_object(id=order_product_data.get('order_product_id'), session=session)
                    campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=int(campaign_product_id_str), session=session)
                    campaign_product_qty_tuples.append((campaign_product,order_product_info.get('qty')))

                    try:
                        ret = rule.rule_checker.pre_order_rule_checker.OrderProductCheckoutRuleChecker.check(
                            check_list=[
                                rule.check_rule.order_product_check_rule.OrderProductCheckRule.is_stock_avaliable_for_checkout   
                            ] , **{
                            'campaign_product':campaign_product,
                            'order_product':order_product,
                        })
                    except Exception:
                        cls._delete_product(pre_order, campaign_product, order_product, api_user, session)  #product sold out
                        print(traceback.format_exc())
                        success = False
                        continue

                    if qty_difference := ret.get('qty_difference'):                                         #product qty not enough 
                        qty = ret.get('qty')
                        cls._update_product(pre_order, order_product, campaign_product, qty, qty_difference, api_user, session)
                        success = False

                if not success:
                    return False, pre_order

                for campaign_product, qty in campaign_product_qty_tuples:    #second loop update qty_add_to_cart -> qty_pending_payment
                    campaign_product.checkout( qty, sync=False, session = session)


                order_data = pre_order.data.copy()

                del order_data['_id']
                order_data['buyer_id'] = api_user.id if api_user else None

                order = database.lss.order.Order.create_object(session=session, **order_data)
                database.lss.order_product.OrderProduct.transfer_to_order(pre_order=pre_order, order=order, session=session)
                pre_order.update(session=session, sync=False, products={},total=0,subtotal=0,discount=0, adjust_price=0, adjust_title="", free_delivery=False, history={}, meta={},applied_discount={})
                
        return True, order

    @classmethod
    @lib.error_handle.error_handler.add_or_update_by_comment_error_handler.add_or_update_by_comment_error_handler
    def add_or_update_by_comment(cls, pre_order, campaign_product_data, qty):
        if not campaign_product_data.get('status'):
            return RequestState.INVALID_PRODUCT_NOT_ACTIVATED
        if campaign_product_data.get('max_order_amount') and \
                qty > campaign_product_data.get('max_order_amount'):
            return RequestState.INVALID_EXCEED_MAX_ORDER_AMOUNT

        if str(campaign_product_data.get('id')) not in pre_order.data.get('products',{}):
            if qty > 0:
                cls.add_product_by_comment(
                        pre_order.id, campaign_product_data.get('id'), qty)
                return RequestState.ADDED
            elif qty == 0:
                return RequestState.INVALID_ADD_ZERO_QTY
            else:
                return RequestState.INVALID_NEGATIVE_QTY

        else:
            if qty > 0:
                if not campaign_product_data.get('customer_editable'):
                    return RequestState.INVALID_EDIT_NOT_ALLOWED

                cls.update_product_by_comment(pre_order.id, campaign_product_data.get('id'), qty)
                return RequestState.UPDATED
            elif qty == 0:
                if not campaign_product_data.get('customer_removable'):
                    return RequestState.INVALID_REMOVE_NOT_ALLOWED
                cls.delete_product_by_comment(
                        pre_order.id, campaign_product_data.get('id'))
                return RequestState.DELETED
            else:
                return RequestState.INVALID_NEGATIVE_QTY


    
                

    

    
    @classmethod
    def summarize_pre_order(cls, pre_order, campaign, save=False):

        #compute discount
        lib.helper.discount_helper.make_discount_for_pre_order(pre_order)

        #compute shipping_cost
        if pre_order.shipping_method == models.order.order.SHIPPING_METHOD_PICKUP:
            pre_order.shipping_cost = 0
        else:
            delivery_charge = float(campaign.meta_logistic.get('delivery_charge',0))
            meta_logistic = campaign.meta_logistic
            delivery_options = meta_logistic.get('additional_delivery_options')

            is_subtotal_over_free_delivery_threshold = pre_order.subtotal >= float(meta_logistic.get('free_delivery_for_order_above_price')) if meta_logistic.get('is_free_delivery_for_order_above_price') else False
            is_items_over_free_delivery_threshold = len(pre_order.products) >= float(meta_logistic.get('free_delivery_for_how_many_order_minimum')) if meta_logistic.get('is_free_delivery_for_how_many_order_minimum') else False

            if(type(pre_order.shipping_option_index)==int):
                if pre_order.shipping_option_data.get('type') == '+':
                    delivery_charge += float(pre_order.shipping_option_data.get('price')) 

                elif pre_order.shipping_option_data.get('type') == '=':
                    delivery_charge =  float(pre_order.shipping_option_data.get('price'))


            if pre_order.free_delivery :
                delivery_charge = 0
            if is_subtotal_over_free_delivery_threshold:
                delivery_charge = 0
                pre_order.meta['subtotal_over_free_delivery_threshold'] = True
            if is_items_over_free_delivery_threshold:
                delivery_charge = 0
                pre_order.meta['items_over_free_delivery_threshold'] = True
            
            pre_order.shipping_cost = delivery_charge

        #summarize_total
        total = 0
        total += pre_order.subtotal
        total -= pre_order.discount
        total = max(total, 0)
        if not pre_order.free_delivery:
            total += pre_order.shipping_cost
        total += pre_order.adjust_price

        pre_order.total = max(total, 0)

        if save:
            pre_order.save()

        return pre_order



    
    # @classmethod
    # def summarize_pre_order(cls, pre_order, campaign, shipping_option=None, save=False):

    #     after_discount_subtotal, discount = lib.helper.discount_helper.make_discount(pre_order.subtotal, pre_order.applied_discount)
    #     pre_order.discount = discount
        
    #     if pre_order.shipping_method == models.order.order.SHIPPING_METHOD_PICKUP:
    #         pre_order.shipping_cost = 0
    #         pre_order.total = 0 if (after_discount_subtotal + pre_order.adjust_price) < 0 else (after_discount_subtotal + pre_order.adjust_price)
    #         if save:
    #             pre_order.save()
    #             return pre_order
    #         return


    #     delivery_charge = float(campaign.meta_logistic.get('delivery_charge',0))
    #     meta_logistic = campaign.meta_logistic
    #     delivery_options = meta_logistic.get('additional_delivery_options')

    #     is_subtotal_over_free_delivery_threshold = pre_order.subtotal >= float(meta_logistic.get('free_delivery_for_order_above_price')) if meta_logistic.get('is_free_delivery_for_order_above_price') else False
    #     is_items_over_free_delivery_threshold = len(pre_order.products) >= float(meta_logistic.get('free_delivery_for_how_many_order_minimum')) if meta_logistic.get('is_free_delivery_for_how_many_order_minimum') else False


    #     if (pre_order.shipping_option_index != None and delivery_options[pre_order.shipping_option_index] ):
    #         option = delivery_options[pre_order.shipping_option_index]

    #         if option.get('type') == '+':
    #             delivery_charge += float(option.get('price')) 

    #         elif option.get('type') == '=':
    #             delivery_charge =  float(option.get('price'))

    #     if pre_order.free_delivery :
    #         delivery_charge = 0
    #     if is_subtotal_over_free_delivery_threshold:
    #         delivery_charge = 0
    #         pre_order.meta['subtotal_over_free_delivery_threshold'] = True
    #     if is_items_over_free_delivery_threshold:
    #         delivery_charge = 0
    #         pre_order.meta['items_over_free_delivery_threshold'] = True
        
    #     pre_order.shipping_cost = delivery_charge
    #     total = after_discount_subtotal + pre_order.adjust_price + delivery_charge
    #     if total < 0:
    #         pre_order.total  = 0
    #         pre_order.discount -= -total
    #     else:
    #         pre_order.total = total
        
    #     if save:
    #         pre_order.save()
    #         return pre_order


class OrderHelper():
    @classmethod
    @lang_translate_default_en
    def get_confirmation_email_content(cls, order, lang=None):
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
        mail_content += f'<h1 data-key="1468266_heading" style="text-align:center; font-family: Georgia,serif,\'Playfair Display\'; font-size: 28px; line-height: 46px; font-weight: 700; color: #4b4b4b; text-transform: none; background-color: #ffffff; margin: 0;">Thanks for Ordering:</h1>'
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
                            <tr style="height: 42px">\
                            </tr>\
                            <tr>\
                                <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/ORDER_DATE') + f' : {date_time} </td>\
                            </tr>'
        try:
            if order.customer_name not in ['undefined', '']:
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
                            </tr>\
                            <tr>'
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

        mail_content+= f'<tr>\
                            <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('REPORT/COLUMN_TITLE/PAYMENT_METHOD') + f' : {order.payment_method}</td>\
                        </tr>'

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

    @lang_translate_default_en
    def i18n_get_mail_subject(order, lang=None):
        return _('EMAIL/ORDER_PLACED/SUBJECT{order_id}{campaign_title}').format(order_id=order.id, campaign_title=order.campaign.title)

    @classmethod
    @lang_translate_default_en
    def get_checkout_email_content(cls, order, order_oid, lang=None):
        price_unit={
            "1":"",
            "1000":"K",
            "1000000":"M"
        }
        order_detail_link = f"{settings.GCP_API_LOADBALANCER_URL}/buyer/order/{order_oid}"
        date_time = order.created_at.strftime("%b %d %Y")

        if 'code' not in order.applied_discount:
            discount_code = ''
        else:
            discount_code = str(order.applied_discount['code'])

        mail_content = f'<div style="width:100%; background: #eaeaea; font-family: \'Open Sans\', sans-serif;"><div style="margin: auto; padding:1%; max-width:900px; background: #ffffff;">'
        mail_content += '<h1 data-key="1468266_heading" style="text-align:center; font-family: Georgia,serif,\'Playfair Display\'; font-size: 28px; line-height: 46px; font-weight: 700; color: #4b4b4b; text-transform: none; background-color: #ffffff; margin: 0;">' + _('EMAIL/ORDER_PLACED/TITLE') + '</h1>'
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
                            <tr style="height: 35px">\
                            </tr>\
                            <tr>\
                                <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/ORDER_DATE') + f' : {date_time} </td>\
                            </tr>'
        mail_content +=     '<tr>\
                                <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/RECEIVER') + f' : {order.shipping_first_name} {order.shipping_last_name}</td>\
                            </tr>\
                            <tr>\
                                <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('REPORT/COLUMN_TITLE/SHIPPING_PHONE') + f' : {order.shipping_phone}</td>\
                            </tr>\
                            <tr>\
                                <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/ORDER_CONFIRM/SHIPPING_METHOD') + f' : {order.shipping_method}</td>\
                            </tr>'
        # mail_content = f'<h3>Order # {str(order.id)}</h3>'
        # mail_content+= f'<h3>{order.campaign.title}</h3>----------------------------------------<br>'
        # mail_content+= f'<b>Customer Name : </b>{order.customer_name}<br>'
        # mail_content+= f'<b>Delivery To : </b><br>' 
        # mail_content+= f'{order.shipping_first_name} {order.shipping_last_name}<br>'
        # mail_content+= f'{order.shipping_phone}<br>'
        # mail_content+= f'<b>Delivery way : </b>{order.shipping_method}<br>'

        try:
            if order.shipping_method == 'pickup':
                mail_content+= f'<tr>\
                                    <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('REPORT/COLUMN_TITLE/PICK_UP_STORE') + f' : {order.shipping_option} ,  {order.pickup_address}</td>\
                                </tr>'
            else:
                mail_content+= f'<tr>\
                                    <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top">' + _('EMAIL/DELIVERY_CONFIRM/DELIVERY_ADDRESS') + f' : {order.shipping_address_1}, {order.shipping_location}, {order.shipping_region}, {order.shipping_postcode}</td>\
                                </tr>'
        except:
            pass
        # try:
        #     if order.shipping_method == 'pickup':
        #         mail_content+= f'<b>Pick up store : </b>{order.shipping_option} ,  {order.pickup_address}<br>'
        #         # mail_content+= f'<b>Pick up date : </b>{meta["pick_up_date"]}<br><br>'
        #     else:
        #         mail_content+= f'<b>Delivery address : </b>{order.shipping_address_1}, {order.shipping_location}, {order.shipping_region}, {order.shipping_postcode}<br>'
        #         # mail_content+= f'<b>Delivery date : </b>{order_data["shipping_date"].strftime("%m/%d/%Y")}<br><br>'
        # except:
        #     pass

        mail_content+=  f'<tr>\
                            <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top"> <a href="{order_detail_link}">' + _('EMAIL/ORDER_CONFIRM/PROCESS_PAYMENT') + f' : </a></td>\
                        </tr>\
                        <tr>\
                            <td style="color: #4b4b4b; font-weight: 600; width: 35%; text-align:left;" valign="top"> <a href="{order_detail_link}"> {order_detail_link} </a></td>\
                        </tr>'
        # mail_content+= f"<a href='{order_detail_link}'>Order Detail Link </a><br>"
        # mail_content+= f"<a href='{order_detail_link}'>{order_detail_link} </a><br>"

        mail_content +=     '</tbody>\
                        </table>'

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
        # mail_content+= '<table style="border-collapse: collapse;"><tr><th style="border: 1px solid black;">Item</th><th style="border: 1px solid black;">Price</th><th style="border: 1px solid black;">Qty</th><th style="border: 1px solid black;">Totoal</th></tr>'
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
        # mail_content+= 'Total : $' + str("%.2f" % float(order.total))+'<br>'

        mail_content += '<div style="background-color: #f5f5f5; max-width: 100%; padding: 13px 52px; font-size: 0.8rem; margin-top: 5%; text-align: center;">\
                  <p>(*)' + _('EMAIL/DELIVERY_CONFIRM/DO_NOT_REPLY_1') + '</p>\
                  <p>' + _('EMAIL/DELIVERY_CONFIRM/DO_NOT_REPLY_2') + '</p></div></div></div></div>'

        return mail_content 

    # @classmethod
    # @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    # def check_expired(cls, order_id):
    #     with database.lss.util.start_session() as session:
    #         with session.start_transaction():

    #             order = database.lss.order.Order.get_object(id=order_id,session=session)


    #             for campaign_product_id_str, order_product_data in order.data.get('products',{}).items():
    #                 order_product = database.lss.order_product.OrderProduct.get_object(id=order_product_data.get('order_product_id'), session=session)
    #                 campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=int(campaign_product_id_str), session=session)

    #                 try:
    #                     ret = rule.rule_checker.pre_order_rule_checker.OrderProductCheckoutRuleChecker.check(**{
    #                         'campaign_product':campaign_product,
    #                         'order_product':order_product,
    #                     })
    #                 except Exception:
    #                     order.update(status=models.order.order.STATUS_EXPIRED,session=session)
    #                     return False, order

    #     return True, order

    
    @classmethod
    @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    def sold_campaign_product(cls, order_id):

        sold_campaign_products=[]

        with database.lss.util.start_session() as session:
            with session.start_transaction():

                order = database.lss.order.Order.get_object(id=order_id,session=session)

                for campaign_product_id_str, order_product_data in order.data.get('products',{}).items():
                    campaign_product = database.lss.campaign_product.CampaignProduct(id=int(campaign_product_id_str))
                    campaign_product.sold(order_product_data.get('qty'), session=session)
                    sold_campaign_products.append(campaign_product)
                    

        for campaign_product in sold_campaign_products:
            product_data = {
                        "id": campaign_product.id,
                        'qty_sold': campaign_product.data.get('qty_sold'),
                        "qty_add_to_cart":campaign_product.data.get('qty_add_to_cart'),
                    }
            service.channels.campaign.send_product_data(campaign_product.data.get("campaign_id"), product_data)
            
            
def adjust_decimal_places(num,decimal_places):
  if decimal_places == 0:
    return floor((num * (10 ** decimal_places))) // (10 ** decimal_places)
  else:
    return floor((num * (10 ** decimal_places))) / (10 ** decimal_places)
