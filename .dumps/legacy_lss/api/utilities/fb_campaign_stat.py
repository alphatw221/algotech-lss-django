from api.utilities.api_orm_utilities import *


def update_fb_campaign_stat(fb_campaign_id):
    fb_campaign = orm_get_fb_campaign(fb_campaign_id)
    if not fb_campaign:
        return

    fb_campaign_stat = orm_get_fb_campaign_stat(fb_campaign_id)
    if not fb_campaign_stat:
        fb_campaign_stat = FBCampaignStat(
            fb_campaign_id=fb_campaign_id,
            total_orders=0,
            total_revenue=0,
            paid_orders=0,
            paid_revenue=0,
            credit_card_orders=0,
            credit_card_revenue=0,
            pay_now_orders=0,
            pay_now_revenue=0,
            unpaid_orders=0,
            unpaid_revenue=0
        )
        db.session.add(fb_campaign_stat)

    def _update_fb_campaign_stat_updater(fb_campaign_stat):
        credit_card_orders = 0
        credit_card_revenue = 0
        pay_now_orders = 0
        pay_now_revenue = 0
        unpaid_orders = 0
        unpaid_revenue = 0

        orders = orm_get_orders(fb_campaign_id)
        if not orders:
            orders = []

        for order in orders:
            if order.order_status == 'cart':
                unpaid_orders += 1
                unpaid_revenue += order.total
            elif order.order_status == 'process':
                order_meta = orm_get_order_metas(
                    order_id=order.id,
                    meta_key='payment_method'
                )
                if not order_meta:
                    continue

                payment_method = getattr(order_meta[0], 'meta_value', None)
                if payment_method == 'credit_card':
                    credit_card_orders += 1
                    credit_card_revenue += order.total
                elif payment_method == 'paynow':
                    pay_now_orders += 1
                    pay_now_revenue += order.total

        # update all the valnue of the row
        fb_campaign_stat.unpaid_orders = unpaid_orders
        fb_campaign_stat.unpaid_revenue = unpaid_revenue
        fb_campaign_stat.credit_card_orders = credit_card_orders
        fb_campaign_stat.credit_card_revenue = credit_card_revenue
        fb_campaign_stat.pay_now_orders = pay_now_orders
        fb_campaign_stat.pay_now_revenue = pay_now_revenue
        fb_campaign_stat.paid_orders = credit_card_orders + pay_now_orders
        fb_campaign_stat.paid_revenue = credit_card_revenue + pay_now_revenue
        fb_campaign_stat.total_orders = fb_campaign_stat.paid_orders + unpaid_orders
        fb_campaign_stat.total_revenue = fb_campaign_stat.paid_revenue + unpaid_revenue

    _update_fb_campaign_stat_updater(fb_campaign_stat)

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return

    return {"campaign id": int(fb_campaign_id),
            "total_orders": fb_campaign_stat.total_orders,
            "total_revenue": fb_campaign_stat.total_revenue}
