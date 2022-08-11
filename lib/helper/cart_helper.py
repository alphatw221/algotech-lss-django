from api import models

import traceback
import database

import lib

class CartHelper():

    @classmethod
    @lib.error_handle.error_handler.pymongo_error_handler.pymongo_error_handler
    def checkout(api_user, campaign_id, cart_id):

         with database.lss.util.start_session() as session:
            with session.start_transaction():
                success = True

                cart = database.lss.cart.Cart.get_object(id=cart_id,session=session)

                campaign_products = database.lss.campaign_product.filter(campaign_id=campaign_id, session=session)  #cache this data in the future
                campaign_product_dict = {campaign_product.get('id'):campaign_product for campaign_product in campaign_products}
                
                order_products = {}
                subtotal = 0
                total = 0
                for campaign_product_id, data in cart.data.get('products',{}).copy().items():
                    try:
                        qty = data['qty']
                        assert type(qty)==int
                        
                        campaign_product = campaign_product_dict[campaign_product_id]
                        campaign_product_price = campaign_product['price']
                        qty_avaliable = campaign_product['qty_for_sale']-campaign_product['qty_sold']
                        if qty>qty_avaliable:
                            qty = qty_avaliable
                            cart.data.get('products',{}).get(campaign_product_id)['qty']=qty
                            success = False
                        

                        order_products[campaign_product_id]={
                            "qty":qty,
                            "type":campaign_product.get("type"),
                            "name":campaign_product.get("name"),
                            "price":campaign_product_price,
                            "image":campaign_product.get("image"),
                            "subtotal":float(qty*campaign_product_price),
                        }

                        subtotal+=campaign_product_price*qty
                    except Exception:
                        print(traceback.format_exc())
                        del cart.data.get('products',{})[campaign_product_id]
                        success = False
                        continue
                
                total = subtotal
                for index, adjust in enumerate(cart.data.get('seller_adjust',[]).copy()):
                    try:
                        title = adjust['title']
                        _type = adjust['type']
                        amount = adjust['amount']

                        assert type in models.cart.cart.SELLER_ADJUST_TYPES
                        assert type(amount) == int

                        if _type == models.cart.cart.SELLER_ADJUST_ADD:
                            total+=amount
                        elif _type == models.cart.cart.SELLER_ADJUST_DISCOUNT:
                            total-=amount
                    except Exception:
                        print(traceback.format_exc())
                        del cart.data.get('seller_adjust',[])[index]
                        success = False
                        continue
                
                if not success:
                    cart.update(session=session, sync=False, **cart.data)
                    return False, None

                
                order_data = cart.data.copy()
                order_data['products']=order_products
                order_data['buyer_id'] = api_user.id if api_user else None
                order_data['subtotal'] = subtotal
                order_data['total'] = total

                order = database.lss.order.Order.create_object(session=session, **order_data)

                cart.clear(session=session)
                return True, order

    