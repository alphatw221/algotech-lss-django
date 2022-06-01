

class PreOrderHelper():


    
    
    @classmethod
    def summarize_pre_order(cls, pre_order, campaign, shipping_option=None, shipping_method=None , save=False):

        if shipping_method and shipping_method == 'in_store':
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

        if (shipping_option and delivery_titles and delivery_types and delivery_prices ):
            addition_delivery_index = delivery_titles.index(shipping_option)

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

        pre_order.total = pre_order.subtotal + pre_order.adjust_price + delivery_charge
        
        if save:
            pre_order.save()
            return pre_order
