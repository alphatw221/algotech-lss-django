

class PreOrderHelper():


    
    
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
        
        is_subtotal_over_free_delivery_threshold = pre_order.subtotal >= float(free_delivery_for_order_above_price)
        is_items_over_free_delivery_threshold = len(pre_order.products) >= float(free_delivery_for_how_many_order_minimum)

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

