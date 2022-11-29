from api import models
from api_v2 import rule
import traceback
import database
from lib.error_handle.error_handler import cart_operation_error_handler
from lib.error_handle.error import cart_error
import service

from datetime import datetime

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
    SERVER_BUSY = 'server_busy'

class CartHelper():


    @classmethod
    def update_cart_product(cls, api_user, cart, campaign_product, qty):

        ret = rule.rule_checker.cart_rule_checker.RuleChecker.check(check_list=[
            rule.check_rule.cart_check_rule.CartCheckRule.is_qty_valid,
        ],**{
            'qty':qty,
        })
        qty = ret.get('qty')
        
        original_qty = cart.products.get(str(campaign_product.id),0)
        qty_difference = qty-original_qty

        ret = rule.rule_checker.cart_rule_checker.RuleChecker.check(check_list=[
            rule.check_rule.cart_check_rule.CartCheckRule.is_cart_lock,
            rule.check_rule.cart_check_rule.CartCheckRule.is_campaign_product_editable,
            rule.check_rule.cart_check_rule.CartCheckRule.is_campaign_product_removeable,
            rule.check_rule.cart_check_rule.CartCheckRule.is_under_max_limit,
        ],**{
            'api_user':api_user,
            'cart':cart,
            'qty':qty,
            'campaign_product':campaign_product,
            'qty_difference':qty_difference
        })


        if not cls.__check_stock_avaliable_and_add_to_cart_by_api(campaign_product.__dict__, qty_difference):
            raise cart_error.CartErrors.UnderStock('out_of_stock') 

        pymongo_cart = database.lss.cart.Cart(id=cart.id)
        cls.__update_cart_product(   #pymongo_cart sync here
            api_user, 
            pymongo_cart,
            campaign_product.__dict__,
            qty
        )

        cls.send_cart_websocket_data(pymongo_cart)
        cls.send_campaign_product_websocket_data(campaign_product.__dict__)


    @classmethod
    @cart_operation_error_handler.update_cart_product_by_comment_error_handler
    def update_cart_product_by_comment(cls, pymongo_cart, campaign_product_data, qty):

        state = None
        if not campaign_product_data.get('active'):
            return RequestState.INVALID_PRODUCT_NOT_ACTIVATED
        if campaign_product_data.get('max_order_amount') and \
                qty > campaign_product_data.get('max_order_amount'):
            return RequestState.INVALID_EXCEED_MAX_ORDER_AMOUNT

        if str(campaign_product_data.get('id')) not in pymongo_cart.data.get('products',{}):
            if qty > 0:
                state =  RequestState.ADDED
            elif qty == 0:
                return RequestState.INVALID_ADD_ZERO_QTY
            else:
                return RequestState.INVALID_NEGATIVE_QTY

        else:
            if qty > 0:
                if not campaign_product_data.get('customer_editable'):
                    return RequestState.INVALID_EDIT_NOT_ALLOWED

                state =  RequestState.UPDATED
            elif qty == 0:
                if not campaign_product_data.get('customer_removable'):
                    return RequestState.INVALID_REMOVE_NOT_ALLOWED
                
                state =  RequestState.DELETED
            else:
                return RequestState.INVALID_NEGATIVE_QTY

        if not cls.__check_stock_avaliable_and_add_to_cart_by_comment(campaign_product_data, pymongo_cart, qty):
            return RequestState.INSUFFICIENT_INV

        cls.__update_cart_product(None, pymongo_cart, campaign_product_data, qty)
        cls.send_cart_websocket_data(pymongo_cart)
        cls.send_campaign_product_websocket_data(campaign_product_data)


        return state

    @classmethod
    def clear(cls, cart):    

        ## in case we need to do something else in the future

        pymongo_cart, pymongo_campaign_products = cls.__clear_cart_and_return_campaign_product(cart)
        for pymongo_campaign_product in pymongo_campaign_products:
            cls.send_campaign_product_websocket_data(pymongo_campaign_product=pymongo_campaign_product)
        cls.send_cart_websocket_data(pymongo_cart)

        ## in case we need to do something else in the future

    @classmethod
    def __clear_cart_and_return_campaign_product(cls, cart, attempts=3):

        try:
            with database.lss.util.start_session() as session:
                with session.start_transaction():
                    campaign_products = []
                    for campaign_product_id_str, qty in cart.products.items():
                        campaign_product = database.lss.campaign_product.CampaignProduct(id=int(campaign_product_id_str))
                        campaign_product.customer_return(qty, sync=True, session=session)
                        campaign_products.append(campaign_product)
                    pymongo_cart = database.lss.cart.Cart(id=cart.id)
                    pymongo_cart.clear(sync=True, session=session)

                    return pymongo_cart, campaign_products

        except Exception:
            if attempts > 0:
                return cls.__clear_cart_and_return_campaign_product(cart, attempts=attempts-1)
            else:
                print(traceback.format_exc())
                raise cart_error.CartErrors.ServerBusy('server_busy')


    @classmethod
    def checkout(cls, api_user, campaign, cart_id, point_discount_processor, shipping_data={}):

        #transfer cart to order ( transaction required )
        success, data = cls.__transfer_cart_to_order(api_user, cart_id, shipping_data)
        if not success:
            error_products_data = data.get('error_products_data', [])
            pymongo_cart = data.get('pymongo_cart')
            
            for error_product_data in error_products_data:
                cls.send_campaign_product_websocket_data(error_product_data)
            cls.send_cart_websocket_data(pymongo_cart)
            
            return False, None

        pymongo_order = data.get('pymongo_order')
        pymongo_cart = data.get('pymongo_cart')
        campaign_product_data_dict = data.get('campaign_product_data_dict')
        is_new_customer = cls.__is_new_customer(campaign, api_user)

        #summarize order (discount, points , shippings fee computing happen here)
        cls.__summarize_order(api_user, campaign, pymongo_order, campaign_product_data_dict, point_discount_processor, is_new_customer = is_new_customer)

        #add new customer
        if is_new_customer:
            campaign.user_subscription.customers.add(api_user)

        #push data to frontend
        for campaign_product_id_str, qty in pymongo_order.data.get('products',{}).copy().items():
            campaign_product_data = campaign_product_data_dict[campaign_product_id_str]
            cls.send_campaign_product_websocket_data(campaign_product_data)
        cls.send_cart_websocket_data(pymongo_cart)

        return True, pymongo_order

    @classmethod
    def __transfer_cart_to_order(cls, api_user, cart_id, shipping_data, attempts=3):
        try:
            with database.lss.util.start_session() as session:
                with session.start_transaction():
                    success = True

                    pymongo_cart = database.lss.cart.Cart.get_object(id=cart_id,session=session)
                    campaign_product_data_dict={}

                    error_products_data = []
                    for campaign_product_id_str, qty in pymongo_cart.data.get('products',{}).copy().items():
                        campaign_product_data = database.lss.campaign_product.CampaignProduct.get(id=int(campaign_product_id_str), session=session)
                        campaign_product_data_dict[campaign_product_id_str]=campaign_product_data
                        try:
                            qty_avaliable = campaign_product_data.get('qty_for_sale')-campaign_product_data.get('qty_sold')-campaign_product_data.get('qty_pending_payment')

                            if qty < 1:
                                del pymongo_cart.data.get('products',{})[campaign_product_id_str] 
                                database.lss.campaign_product.CampaignProduct(id=campaign_product_data.get('id')).customer_return(qty, sync=False, session=session)
                                error_products_data.append({'id':campaign_product_data.get('id')})
                                success = False
                                continue

                            if campaign_product_data.get('oversell')==True:
                                continue

                            if qty_avaliable < 1 :
                                del pymongo_cart.data.get('products',{})[campaign_product_id_str] 
                                database.lss.campaign_product.CampaignProduct(id=campaign_product_data.get('id')).customer_return(qty, sync=False, session=session)
                                error_products_data.append({'id':campaign_product_data.get('id')})
                                success = False
                                continue

                            if qty>qty_avaliable :
                                return_qty = qty - qty_avaliable
                                pymongo_cart.data.get('products',{})[campaign_product_id_str] = qty_avaliable
                                database.lss.campaign_product.CampaignProduct(id=campaign_product_data.get('id')).customer_return(return_qty, sync=False, session=session)
                                error_products_data.append({'id':campaign_product_data.get('id')})
                                success = False
                            
                        except Exception:
                            print(traceback.format_exc())
                            del pymongo_cart.data.get('products',{})[campaign_product_id_str]
                            database.lss.campaign_product.CampaignProduct(id=campaign_product_data.get('id')).customer_return(qty, sync=False, session=session)
                            error_products_data.append({'id':campaign_product_data.get('id')})
                            success = False

                    if not success:
                        pymongo_cart.update(session=session, sync=True, **pymongo_cart.data)
                        return False, {'pymongo_cart':pymongo_cart, 'error_products_data':error_products_data, }

                    pymongo_cart.data['buyer_id']=api_user.id if api_user else None
                    pymongo_order = database.lss.order.Order.create_object(
                        session=session,
                        **pymongo_cart.data, 
                        **shipping_data,
                        
                        )  

                    for campaign_product_id_str, qty in pymongo_order.data.get('products',{}).copy().items():
                        campaign_product_data = campaign_product_data_dict[campaign_product_id_str]
                        order_product_data={
                            "name":campaign_product_data.get('name'),
                            "sku":campaign_product_data.get('sku'),
                            "price":campaign_product_data.get('price'),
                            "image":campaign_product_data.get('image'),
                            "qty":qty,
                            "type":campaign_product_data.get('type'),
                            "subtotal":campaign_product_data.get('price')*qty,
                            #relation:
                            "order_id":pymongo_order.id,
                            "campaign_product_id":int(campaign_product_id_str)
                        }
                        database.lss.order_product.OrderProduct.create(session=session, **order_product_data)
                        campaign_product = database.lss.campaign_product.CampaignProduct(id=int(campaign_product_id_str))
                        campaign_product.checkout(qty=qty, sync=True, session=session)
                        campaign_product_data_dict[campaign_product_id_str] = campaign_product.data

                    pymongo_cart.clear(session=session, sync=True)
            
            return True, {'pymongo_order':pymongo_order, 'campaign_product_data_dict':campaign_product_data_dict, 'pymongo_cart':pymongo_cart}

        except Exception:
            if attempts > 0:
                cls.__transfer_cart_to_order(api_user, cart_id, shipping_data, attempts=attempts-1)
            else:
                print(traceback.format_exc())
                raise cart_error.CartErrors.ServerBusy('server_busy')

    @staticmethod
    def __is_new_customer(campaign, api_user):
        return True if api_user and not campaign.user_subscription.customers.filter(id=api_user.id).exists() else False

    @classmethod
    def __summarize_order(cls, api_user, campaign:models.campaign.campaign.Campaign, pymongo_order:database.lss.order.Order, campaign_product_data_dict, point_discount_processor, is_new_customer=False):

        subtotal = 0
        shipping_cost = 0
        total = 0
        meta = {}

        product_category_data_dict={}
        product_category_products_dict = {}
        for campaign_prodcut_id_str, qty in pymongo_order.data.get('products',{}).items():
            campaign_product_data = campaign_product_data_dict.get(campaign_prodcut_id_str,{})

            if len(campaign_product_data.get('categories',[])) == 1 :
                product_category_id_str = campaign_product_data.get('categories',[])[0]
                if product_category_id_str not in product_category_data_dict:
                    product_category_data = database.lss.product_category.ProductCategory.get(id=int(campaign_product_data.get('categories',[])[0]))
                    if product_category_data:
                        product_category_data_dict[product_category_id_str] = product_category_data

                if product_category_products_dict.get(product_category_id_str):
                    product_category_products_dict[product_category_id_str].append({'campaign_product_id':campaign_prodcut_id_str, 'qty':qty})
                else:
                    product_category_products_dict[product_category_id_str] = [{'campaign_product_id':campaign_prodcut_id_str, 'qty':qty}]

            subtotal += campaign_product_data.get('price',0)*qty
        shipping_cost, category_logistic_applied = cls.__compute_shipping_cost(campaign, pymongo_order, product_category_data_dict, product_category_products_dict, campaign_product_data_dict)
        

        #compute free_delivery
        meta_logistic = campaign.meta_logistic
        is_subtotal_over_free_delivery_threshold = subtotal >= float(meta_logistic.get('free_delivery_for_order_above_price')) if meta_logistic.get('is_free_delivery_for_order_above_price') else False
        is_items_over_free_delivery_threshold = len(pymongo_order.data.get('products')) >= float(meta_logistic.get('free_delivery_for_how_many_order_minimum')) if meta_logistic.get('is_free_delivery_for_how_many_order_minimum') else False
        meta['subtotal_over_free_delivery_threshold'] = True if is_subtotal_over_free_delivery_threshold else False
        meta['items_over_free_delivery_threshold'] = True if is_items_over_free_delivery_threshold else False
            

        #compute point discount
        point_discount = point_discount_processor.compute_point_discount() if point_discount_processor else 0
        

        #summarize_total
        total += subtotal
        total -= pymongo_order.data.get('discount',0)
        total -= point_discount
        total = subtotal_after_discount = max(total, 0)
        if pymongo_order.data.get('free_delivery') or is_subtotal_over_free_delivery_threshold or is_items_over_free_delivery_threshold:
            pass
        else:
            total += shipping_cost
        total += pymongo_order.data.get('adjust_price',0)
        total = max(total, 0)
        
        #compute points earned
        points_earned = point_discount_processor.compute_points_earned(subtotal_after_discount) if point_discount_processor else 0
        point_expired_at = point_discount_processor.compute_expired_date() if point_discount_processor else None

        pymongo_order.update(

            price_unit = campaign.price_unit,
            decimal_places = campaign.decimal_places,
            currency = campaign.currency,
            
            subtotal = subtotal,
            shipping_cost = shipping_cost,
            total = total,
            meta = meta,
            points_used = point_discount_processor.points_used if point_discount_processor else 0,
            point_discount = point_discount,
            points_earned = points_earned,
            point_expired_at = point_expired_at,
            meta_point = campaign.meta_point,

            remark = 'new customer' if is_new_customer else '',
            **campaign.user_subscription.meta.get('order_default_fields',{}),
            sync=True)

        if point_discount_processor:
            point_discount_processor.update_wallet(points_earned, point_expired_at, pymongo_order['id'])

    @classmethod 
    def __compute_shipping_cost(cls, campaign, pymongo_order, product_category_data_dict:dict, product_category_products_dict:dict, campaign_product_data_dict:dict):
        if pymongo_order.data.get('shipping_method') == models.order.order.SHIPPING_METHOD_PICKUP:
            return 0, False

        shipping_cost = 0
        category_logistic_applied = False
        for product_category_id_str, product_category_data in product_category_data_dict.items():
            if product_category_data.get('meta_logistic',{}).get('enable_flat_rate')==True:
                category_logistic_applied = True

                is_category_product_subtotal_above = False
                if product_category_data.get('meta_logistic',{}).get('is_free_delivery_for_order_above_price'):
                    category_products_subtotal = 0
                    
                    for category_product in product_category_products_dict.get(product_category_id_str):
                        category_products_subtotal += campaign_product_data_dict.get(category_product.get('campaign_product_id'),{}).get('price') * category_product.get('qty')
                    
                    is_category_product_subtotal_above = category_products_subtotal > product_category_data.get('meta_logistic',{}).get('free_delivery_for_order_above_price',0)

                shipping_cost+=0 if is_category_product_subtotal_above else product_category_data.get('meta_logistic').get('flat_rate',0)
        
        if category_logistic_applied:
            return shipping_cost, True

        shipping_cost = float(campaign.meta_logistic.get('delivery_charge',0))

        if(type(pymongo_order.data.get('shipping_option_index'))==int):
            if pymongo_order.data.get('shipping_option_data',{}).get('type') == '+':
                shipping_cost += float(pymongo_order.data.get('shipping_option_data',{}).get('price',0)) 

            elif pymongo_order.data.get('shipping_option_data',{}).get('type') == '=':
                shipping_cost =  float(pymongo_order.data.get('shipping_option_data',{}).get('price',0))

        return shipping_cost, False

    @classmethod
    def __check_stock_avaliable_and_add_to_cart_by_api(cls, campaign_product_data, qty_difference, attempts=10):

        if qty_difference == 0:
            return True

        if campaign_product_data.get('oversell') == True:
            database.lss.campaign_product.CampaignProduct(id=campaign_product_data.get('id')).add_to_cart(qty=qty_difference, sync=False)
            return True
            
        try:
            with database.lss.util.start_session() as session:
                with session.start_transaction():
                    return cls.__check_stock_avaliable_and_add_to_cart(campaign_product_data, qty_difference, session)
        except Exception:
            if attempts > 0:
                cls.__check_stock_avaliable_and_add_to_cart_by_api(campaign_product_data, qty_difference, attempts=attempts-1)
            else:
                raise cart_error.CartErrors.ServerBusy('server_busy')

    @classmethod
    def __check_stock_avaliable_and_add_to_cart_by_comment(cls, campaign_product_data, pymongo_cart:database.lss.cart.Cart, qty, attempts=10):
        try:
            with database.lss.util.start_session() as session:
                with session.start_transaction():

                    pymongo_cart._sync(session)
                    original_qty = pymongo_cart.data.get('products',{}).get(str(campaign_product_data.get('id')),0)
                    qty_difference = qty-original_qty

                    if qty_difference == 0:
                        return True

                    if campaign_product_data.get('oversell') == True:
                        database.lss.campaign_product.CampaignProduct(id=campaign_product_data.get('id')).add_to_cart(qty=qty_difference, sync=False, session=session)
                        return True

                    return cls.__check_stock_avaliable_and_add_to_cart(campaign_product_data, qty_difference, session)
                    
        except Exception:
            if attempts > 0:
                cls.__check_stock_avaliable_and_add_to_cart_by_comment(campaign_product_data, pymongo_cart, qty, attempts=attempts-1)
            else:
                raise cart_error.CartErrors.ServerBusy('server_busy')

    @staticmethod
    def __check_stock_avaliable_and_add_to_cart(campaign_product_data, qty_difference, session):
        
        
        pymongo_campaign_product = database.lss.campaign_product.CampaignProduct.get_object(id=campaign_product_data.get('id'), session=session)

        if qty_difference < 0:
            pymongo_campaign_product.add_to_cart(qty_difference, sync=False, session=session)
            return True
            
        avaliable_qty = 0
        if campaign_product_data.get('overbook'):
            avaliable_qty = pymongo_campaign_product.data.get("qty_for_sale")-pymongo_campaign_product.data.get('qty_sold')-pymongo_campaign_product.data.get('qty_pending_payment')
        else:
            avaliable_qty = pymongo_campaign_product.data.get("qty_for_sale")-pymongo_campaign_product.data.get('qty_sold')-pymongo_campaign_product.data.get('qty_pending_payment')-pymongo_campaign_product.data.get('qty_add_to_cart') 

        if avaliable_qty < qty_difference:
            return False

        pymongo_campaign_product.add_to_cart(qty_difference, sync=False, session=session)
        return True

    @staticmethod
    def __update_cart_product(api_user, pymongo_cart, campaign_product_data, qty):
    
    
        if qty<=0:
            pymongo_cart.remove_product(campaign_product_data.get('id'), sync=True)
        else:
            data ={
                "lock_at": datetime.now() if api_user and api_user.type == 'customer' else None,
                f"products.{str(campaign_product_data.get('id'))}": qty,
            }
            pymongo_cart.update(**data, sync=True)



    @staticmethod
    def send_cart_websocket_data( pymongo_cart):
        service.channels.campaign.send_cart_data(pymongo_cart.data.get('campaign_id'), pymongo_cart.data)
    
    @staticmethod
    def send_campaign_product_websocket_data(campaign_product_data={}, pymongo_campaign_product=None):

        if pymongo_campaign_product:
            campaign_product_data = pymongo_campaign_product.data
        else:
            campaign_product_data = database.lss.campaign_product.CampaignProduct.get(id=campaign_product_data.get('id'))

        product_data = {
            "id": campaign_product_data.get('id'),
            'qty_sold': campaign_product_data.get('qty_sold'),
            'qty_pending_payment':campaign_product_data.get('qty_pending_payment'),
            "qty_add_to_cart":campaign_product_data.get('qty_add_to_cart'),

        }
        service.channels.campaign.send_product_data(campaign_product_data.get("campaign_id"), product_data)



    @staticmethod
    def __compute_point_discount(campaign, points_used):
        return 0  #TODO

    @staticmethod
    def __compute_points_earned(campaign, subtotal):
        return 0 #TODO