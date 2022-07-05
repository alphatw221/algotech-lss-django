from os import sync
from django.conf import settings

from api import rule,models


import lib
import database
import traceback
from datetime import datetime
class PreOrderHelper():

    @classmethod
    @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    def add_product(cls, api_user, pre_order_id, campaign_product_id, qty):

        with database.lss.util.start_session() as session:
            with session.start_transaction():
                pre_order = database.lss.pre_order.PreOrder.get_object(id=pre_order_id,session=session)
                campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=campaign_product_id,session=session)

                ret = rule.rule_checker.pre_order_rule_checker.PreOrderAddProductRuleChecker.check(**{
                    'api_user':api_user,
                    'api_pre_order':pre_order.data,
                    'api_campaign_product':campaign_product.data,
                    'qty':qty,
                    })

                qty = ret.get('qty')
                qty_difference = ret.get('qty_difference')
                
                order_product = database.lss.order_product.OrderProduct.create(
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

                pre_order.update(**data, session=session)
                campaign_product.add_to_cart(qty_difference, sync=False, session=session)
        return pre_order

    @classmethod
    @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    def update_product(cls, api_user, pre_order_id, order_product_id, qty):

        with database.lss.util.start_session() as session:
            with session.start_transaction():

                pre_order = database.lss.pre_order.PreOrder.get_object(id=pre_order_id,session=session)
                order_product = database.lss.order_product.OrderProduct.get_object(id=order_product_id,session=session)
                campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=order_product.data.get('campaign_product_id'),session=session)

                ret = rule.rule_checker.pre_order_rule_checker.PreOrderUpdateProductRuleChecker.check(**{
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
    def _update_product(cls, pre_order, order_product, campaign_product, qty, qty_difference, api_user, session):
        
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
        campaign_product.add_to_cart(qty_difference, sync=False, session=session)
        pre_order.update(**data, session=session)

    @classmethod
    @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    def delete_product(cls, api_user, pre_order_id, order_product_id):

        with database.lss.util.start_session() as session:
            with session.start_transaction():

                pre_order = database.lss.pre_order.PreOrder.get_object(id=pre_order_id,session=session)
                order_product = database.lss.order_product.OrderProduct.get_object(id=order_product_id,session=session)
                campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=order_product.data.get('campaign_product_id'),session=session)

                rule.rule_checker.pre_order_rule_checker.PreOrderDeleteProductRuleChecker.check(**{
                    'api_user':api_user,
                    'api_pre_order':pre_order.data,
                    'api_order_product':order_product.data,
                    'api_campaign_product':campaign_product.data,
                    })
                cls._delete_product(pre_order, campaign_product, order_product, api_user, session)
        return True

    @classmethod
    def _delete_product(cls, pre_order, campaign_product, order_product, api_user, session):
        
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
        campaign_product.customer_return(order_product.data.get('qty'), sync=False, session=session)
        pre_order.delete_product(campaign_product, session=session, sync=False, **data)
        order_product.delete(session=session)
    @classmethod
    @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    def checkout(cls, api_user, campaign_id, pre_order_id):
        with database.lss.util.start_session() as session:
            with session.start_transaction():
                success = True
                campaign = database.lss.campaign.Campaign.get_object(id=campaign_id,session=session)
                pre_order = database.lss.pre_order.PreOrder.get_object(id=pre_order_id,session=session)

                rule.rule_checker.pre_order_rule_checker.PreOrderCheckoutRuleChecker.check(**{
                    'api_user':api_user,
                    'api_pre_order':pre_order.data,
                    'campaign':campaign
                    })

                for campaign_product_id_str in pre_order.data.get('products',{}).keys():
                    order_product_data = pre_order.data.get('products',{}).get(campaign_product_id_str)
                    order_product = database.lss.order_product.OrderProduct.get_object(id=order_product_data.get('order_product_id'), session=session)
                    campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=int(campaign_product_id_str), session=session)

                    try:
                        ret = rule.rule_checker.pre_order_rule_checker.OrderProductCheckoutRuleChecker.check(**{
                            'campaign_product':campaign_product,
                            'order_product':order_product,
                        })
                    except Exception:
                        cls._delete_product(pre_order, campaign_product, order_product, api_user, session)
                        print(traceback.format_exc())
                        success = False
                        continue

                    if qty_difference := ret.get('qty_difference'):
                        qty = ret.get('qty')
                        cls._update_product(pre_order, order_product, campaign_product, qty, qty_difference, api_user, session)
                        success = False

                if not success:
                    return False, pre_order

                for campaign_product_id_str in pre_order.data.get('products',{}).keys():
                    database.lss.campaign_product.CampaignProduct(id=int(campaign_product_id_str)).sold(order_product_data.get('qty'), sync=False, session=session)

                order_data = pre_order.data.copy()

                del order_data['_id']
                order_data['buyer_id'] = api_user.id if api_user else None

                order = database.lss.order.Order.create(session=session, **order_data)
                database.lss.order_product.OrderProduct.transfer_to_order(pre_order=pre_order, order=order, session=session)
                pre_order.update(session=session, sync=False, products={},total=0,subtotal=0, adjust_price=0, adjust_title="", free_delivery=False, history={}, meta={})
                
        return True, order

    
    
    @classmethod
    def summarize_pre_order(cls, pre_order, campaign, shipping_option=None, save=False):

        if pre_order.shipping_method == 'pickup':
            pre_order.shipping_cost = 0
            pre_order.total = pre_order.subtotal + pre_order.adjust_price
            if save:
                pre_order.save()
                return pre_order
            return


        delivery_charge = float(campaign.meta_logistic.get('delivery_charge',0))
        delivery_titles = campaign.meta_logistic.get('additional_delivery_charge_title')
        delivery_types = campaign.meta_logistic.get('additional_delivery_charge_type')
        delivery_prices = campaign.meta_logistic.get('additional_delivery_charge_price')

        free_delivery_for_order_above_price = campaign.meta_logistic.get('free_delivery_for_order_above_price') if campaign.meta_logistic.get('is_free_delivery_for_order_above_price') == 1 else 0
        free_delivery_for_how_many_order_minimum = campaign.meta_logistic.get('free_delivery_for_how_many_order_minimum') if campaign.meta_logistic.get('is_free_delivery_for_how_many_order_minimum') == 1 else 0
        
        is_subtotal_over_free_delivery_threshold = pre_order.subtotal >= float(free_delivery_for_order_above_price) if free_delivery_for_order_above_price else False
        is_items_over_free_delivery_threshold = len(pre_order.products) >= float(free_delivery_for_how_many_order_minimum) if free_delivery_for_how_many_order_minimum else False

        if (pre_order.shipping_option and delivery_titles and delivery_types and delivery_prices ):
            addition_delivery_index = delivery_titles.index(pre_order.shipping_option)

            if delivery_types[addition_delivery_index] == '+':
                delivery_charge += float(delivery_prices[addition_delivery_index]) 

            elif delivery_types[addition_delivery_index] == '=':
                delivery_charge =  float(delivery_prices[addition_delivery_index])

        if pre_order.free_delivery :
            delivery_charge = 0
        if is_subtotal_over_free_delivery_threshold:
            delivery_charge = 0
            pre_order.meta['subtotal_over_free_delivery_threshold'] = True
        if is_items_over_free_delivery_threshold:
            delivery_charge = 0
            pre_order.meta['items_over_free_delivery_threshold'] = True

        total = pre_order.subtotal + pre_order.adjust_price + delivery_charge
        pre_order.total  = 0 if total<0 else total
        pre_order.shipping_cost = delivery_charge
        
        if save:
            pre_order.save()
            return pre_order


class OrderHelper():

    @classmethod
    def get_confirmation_email_content(cls, order, lang=None):
        mail_content = f'<h3>Order # {str(order.id)}</h3>'
        mail_content+= f'<h3>{order.campaign.title}</h3>----------------------------------------<br>'
        mail_content+= f'<b>Customer Name : </b>{order.customer_name}<br>'
        mail_content+= f'<b>Delivery To : </b><br>' 
        mail_content+= f'{order.shipping_first_name} {order.shipping_last_name}<br>'
        mail_content+= f'{order.shipping_phone}<br>'
        mail_content+= f'<b>Delivery way : </b>{order.shipping_method}<br>'
        try:
            if order.shipping_method == 'pickup':
                mail_content+= f'<b>Pick up store : </b>{order.shipping_option} ,  {order.pickup_address}<br>'
                # mail_content+= f'<b>Pick up date : </b>{meta["pick_up_date"]}<br><br>'
            else:
                mail_content+= f'<b>Delivery address : </b>{order.shipping_address_1}, {order.shipping_location}, {order.shipping_region}, {order.shipping_postcode}<br>'
                # mail_content+= f'<b>Delivery date : </b>{order_data["shipping_date"].strftime("%m/%d/%Y")}<br><br>'
        except:
            pass

        mail_content+= f'<b>Payment method : </b>{order.payment_method}<br>'
        mail_content+= '<table style="border-collapse: collapse;"><tr><th style="border: 1px solid black;">Item</th><th style="border: 1px solid black;">Price</th><th style="border: 1px solid black;">Qty</th><th style="border: 1px solid black;">Totoal</th></tr>'
        for key, product in order.products.items():
            mail_content+= f'<tr><td style="border: 1px solid black;">{product["name"]}</td><td style="border: 1px solid black;">${product["price"]}</td><td style="border: 1px solid black;">{product["qty"]}</td><td style="border: 1px solid black;">{product["subtotal"]}</td></tr>'
        mail_content+= '</table>'
        
        mail_content+= '<br>Delivery Charge: ' 
        mail_content+= '$'+ str("%.2f" % float(order.shipping_cost))+'<br>'
        mail_content+= 'Total : $' + str("%.2f" % float(order.total))

        return mail_content

    @classmethod
    def get_checkout_email_content(cls, order, order_oid, lang=None):

        order_detail_link = f"{settings.GCP_API_LOADBALANCER_URL}/buyer/order/{order_oid}"

        mail_content = f'<h3>Order # {str(order.id)}</h3>'
        mail_content+= f'<h3>{order.campaign.title}</h3>----------------------------------------<br>'
        mail_content+= f'<b>Customer Name : </b>{order.customer_name}<br>'
        mail_content+= f'<b>Delivery To : </b><br>' 
        mail_content+= f'{order.shipping_first_name} {order.shipping_last_name}<br>'
        mail_content+= f'{order.shipping_phone}<br>'
        mail_content+= f'<b>Delivery way : </b>{order.shipping_method}<br>'
        try:
            if order.shipping_method == 'pickup':
                mail_content+= f'<b>Pick up store : </b>{order.shipping_option} ,  {order.pickup_address}<br>'
                # mail_content+= f'<b>Pick up date : </b>{meta["pick_up_date"]}<br><br>'
            else:
                mail_content+= f'<b>Delivery address : </b>{order.shipping_address_1}, {order.shipping_location}, {order.shipping_region}, {order.shipping_postcode}<br>'
                # mail_content+= f'<b>Delivery date : </b>{order_data["shipping_date"].strftime("%m/%d/%Y")}<br><br>'
        except:
            pass

        mail_content+= '<table style="border-collapse: collapse;"><tr><th style="border: 1px solid black;">Item</th><th style="border: 1px solid black;">Price</th><th style="border: 1px solid black;">Qty</th><th style="border: 1px solid black;">Totoal</th></tr>'
        for key, product in order.products.items():
            mail_content+= f'<tr><td style="border: 1px solid black;">{product["name"]}</td><td style="border: 1px solid black;">${product["price"]}</td><td style="border: 1px solid black;">{product["qty"]}</td><td style="border: 1px solid black;">{product["subtotal"]}</td></tr>'
        mail_content+= '</table>'
        
        mail_content+= '<br>Delivery Charge: ' 
        mail_content+= '$'+ str("%.2f" % float(order.shipping_cost))+'<br>'
        mail_content+= 'Total : $' + str("%.2f" % float(order.total))+'<br>'

        mail_content+= f"<a href='{order_detail_link}'>Order Detail Link </a><br>"
        mail_content+= f"<a href='{order_detail_link}'>{order_detail_link} </a><br>"
        return mail_content


    