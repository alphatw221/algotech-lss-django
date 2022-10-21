from api import models
from api import rule
import traceback
from api.views import campaign
import database
import service
import lib

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
            raise lib.error_handle.error.cart_error.CartErrors.UnderStock('out_of_stock') 

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
    @lib.error_handle.error_handler.cart_operation_error_handler.update_cart_product_by_comment_error_handler
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

        if campaign_product_data.get('oversell'):
            pass
        elif not cls.__check_stock_avaliable_and_add_to_cart_by_comment(campaign_product_data, pymongo_cart, qty):
            return RequestState.INSUFFICIENT_INV

        cls.__update_cart_product(None, pymongo_cart, campaign_product_data, qty)
        cls.send_cart_websocket_data(pymongo_cart)
        cls.send_campaign_product_websocket_data(campaign_product_data)


        return state


    @classmethod
    @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    def checkout(cls, api_user, campaign_id, cart_id, shipping_data={}, attempts=3):

        try:
            with database.lss.util.start_session() as session:
                with session.start_transaction():
                    success = True

                    pymongo_cart = database.lss.cart.Cart.get_object(id=cart_id,session=session)
                    campaign_product_data_dict={}
                    for campaign_product_id_str, qty in pymongo_cart.data.get('products',{}).copy().items():
                        campaign_product_data = database.lss.campaign_product.CampaignProduct.get(id=int(campaign_product_id_str), session=session)
                        campaign_product_data_dict[campaign_product_id_str]=campaign_product_data
                        try:
                            qty_avaliable = campaign_product_data.get('qty_for_sale')-campaign_product_data.get('qty_sold')-campaign_product_data.get('qty_pending_payment')

                            if qty_avaliable < 1 or qty < 1:
                                del pymongo_cart.data.get('products',{})[campaign_product_id_str]     
                                success = False

                            elif qty>qty_avaliable and not campaign_product_data.get('oversell'):
                                pymongo_cart.data.get('products',{})[campaign_product_id_str] = qty_avaliable
                                success = False
                            
                        except Exception:
                            print(traceback.format_exc())
                            del pymongo_cart.data.get('products',{})[campaign_product_id_str]
                            success = False

                    if not success:
                        pymongo_cart.update(session=session, sync=False, **pymongo_cart.data)
                        return False, None

                    
                    pymongo_order = database.lss.order.Order.create_object(
                        session=session,
                        buyer=api_user.id if api_user else None, 
                        **pymongo_cart.data, 
                        **shipping_data)  

                    for campaign_product_id_str, qty in pymongo_order.data.get('products',{}).copy().items():
                        campaign_product_data = campaign_product_data_dict[campaign_product_id_str]
                        order_product_data={
                            "name":campaign_product_data.get('name'),
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
                        database.lss.campaign_product.CampaignProduct(id=int(campaign_product_id_str)).checkout(qty=qty, sync=False, session=session)

                    pymongo_cart.clear(session=session, sync=True)

            #after transaction ends:
            for campaign_product_id_str, qty in pymongo_order.data.get('products',{}).copy().items():
                campaign_product_data = campaign_product_data_dict[campaign_product_id_str]
                cls.send_campaign_product_websocket_data(campaign_product_data)
            cls.send_cart_websocket_data(pymongo_cart)
            
            return True, pymongo_order

        except Exception:
            if attempts > 0:
                cls.checkout(api_user, campaign_id, cart_id, shipping_data, attempts=attempts-1)
            else:
                raise lib.error_handle.error.cart_error.CartErrors.ServerBusy('server_busy')





    @classmethod
    def __check_stock_avaliable_and_add_to_cart_by_api(cls, campaign_product_data, qty_difference, attempts=10):

        if qty_difference == 0:
            return True

        if campaign_product_data.get('oversell'):
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
                raise lib.error_handle.error.cart_error.CartErrors.ServerBusy('server_busy')

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

                    if campaign_product_data.get('oversell'):
                        database.lss.campaign_product.CampaignProduct(id=campaign_product_data.get('id')).add_to_cart(qty=qty_difference, sync=False, session=session)
                        return True

                    return cls.__check_stock_avaliable_and_add_to_cart(campaign_product_data, qty_difference, session)
                    
        except Exception:
            if attempts > 0:
                cls.__check_stock_avaliable_and_add_to_cart_by_comment(campaign_product_data, pymongo_cart, qty, attempts=attempts-1)
            else:
                raise lib.error_handle.error.cart_error.CartErrors.ServerBusy('server_busy')

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
    def send_campaign_product_websocket_data(campaign_product_data):
    
        campaign_product_data = database.lss.campaign_product.CampaignProduct.get(id=campaign_product_data.get('id'))
        product_data = {
            "id": campaign_product_data.get('id'),
            'qty_sold': campaign_product_data.get('qty_sold'),
            'qty_pending_payment':campaign_product_data.get('qty_pending_payment'),
            "qty_add_to_cart":campaign_product_data.get('qty_add_to_cart'),

        }
        service.channels.campaign.send_product_data(campaign_product_data.get("campaign_id"), product_data)



    