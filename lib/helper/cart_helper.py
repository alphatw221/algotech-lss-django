from api import models
from api import rule
import traceback
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


class CartHelper():


    @classmethod
    def update_cart_product(cls, api_user, cart, campaign_product, qty):

        original_qty = cart.products.get(str(campaign_product.id),0)
        qty_difference = qty-original_qty

        ret = rule.rule_checker.cart_rule_checker.RuleChecker.check(check_list=[
            rule.check_rule.cart_check_rule.CartCheckRule.is_cart_lock,
            rule.check_rule.cart_check_rule.CartCheckRule.is_qty_valid,
            rule.check_rule.cart_check_rule.CartCheckRule.campaign_product_type,
            rule.check_rule.cart_check_rule.CartCheckRule.is_campaign_product_editable,
            rule.check_rule.cart_check_rule.CartCheckRule.is_campaign_product_removeable,
            rule.check_rule.cart_check_rule.CartCheckRule.is_stock_avaliable,
            rule.check_rule.cart_check_rule.CartCheckRule.is_under_max_limit,
        ],**{
            'api_user':api_user,
            'cart':cart,
            'qty':qty,
            'campaign_product':campaign_product,
            'qty_difference':qty_difference
        })

        cls.__update_cart_product(
            api_user, 
            database.lss.cart.Cart(id=cart.id),
            campaign_product.__dict__,
            qty,
            qty_difference
        
        )
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

        original_qty = pymongo_cart.data.get('products',{}).get(str(campaign_product_data.get('id')),0)
        qty_difference = qty-original_qty
        rule.check_rule.cart_check_rule.CartCheckRule.is_stock_avaliable(**{
                    "campaign_product_data":campaign_product_data,
                    'qty_difference':qty_difference,
                })
        cls.__update_cart_product(None, pymongo_cart, campaign_product_data, qty, qty_difference)
        return state

    @staticmethod
    def __update_cart_product(api_user, pymongo_cart, campaign_product_data, qty, qty_difference):
    
        
        pymongo_campaign_product = database.lss.campaign_product.CampaignProduct(id=campaign_product_data.get('id'))
        pymongo_campaign_product.add_to_cart(qty_difference, sync=True) 

        if qty<=0:
            pymongo_cart.remove_product(pymongo_campaign_product.id, sync=True)
        else:
            data ={
                "lock_at": datetime.now() if api_user and api_user.type == 'customer' else None,
                f"products.{str(pymongo_campaign_product.id)}": qty,
            }
            pymongo_cart.update(**data, sync=True)

        product_data = {
            "id": pymongo_campaign_product.id,
            'qty_sold': pymongo_campaign_product.data.get('qty_sold'),
            'qty_pending_payment':pymongo_campaign_product.data.get('qty_pending_payment'),
            "qty_add_to_cart":pymongo_campaign_product.data.get('qty_add_to_cart'),

        }
        service.channels.campaign.send_cart_data(campaign_product_data.get("campaign_id"), pymongo_cart.data)
        service.channels.campaign.send_product_data(campaign_product_data.get("campaign_id"), product_data)





    @classmethod
    @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    def checkout(cls, api_user, campaign_id, cart_id, attempts=3):

        try:
            with database.lss.util.start_session() as session:
                with session.start_transaction():
                    success = True

                    pymongo_cart = database.lss.cart.Cart.get_object(id=cart_id,session=session)

                    campaign_products = database.lss.campaign_product.filter(campaign_id=campaign_id, session=session)  #cache this data in the future
                    campaign_product_dict = {str(campaign_product.get('id')):campaign_product for campaign_product in campaign_products}
                    
                    for campaign_product_id, qty in pymongo_cart.data.get('products',{}).copy().items():
                        try:
                            campaign_product = campaign_product_dict[campaign_product_id]
                            qty_avaliable = campaign_product['qty_for_sale']-campaign_product['qty_sold']
                            if qty>qty_avaliable and not campaign_product.get('oversell'):
                                qty = qty_avaliable
                                pymongo_cart.data.get('products',{})[campaign_product_id]=qty
                                success = False
                        except Exception:
                            print(traceback.format_exc())
                            del pymongo_cart.data.get('products',{})[campaign_product_id]
                            success = False

                    if not success:
                        pymongo_cart.update(session=session, sync=False, **pymongo_cart.data)
                        return False, None

                    
                    pymongo_order = database.lss.order.Order.create_object(session=session, **pymongo_cart.data)  

                    #create order product here     with or without session

                    pymongo_cart.clear(session=session)
                    return True, pymongo_order
        except Exception:
            if attempts > 0:
                cls.checkout(api_user, campaign_id, cart_id, attempts=attempts-1)
            else:
                raise
                #server busy , please try again