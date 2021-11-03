from config import db, logger, shopping_cart_init_url
import threading
import traceback
from sqlalchemy.sql import func
# Import models from models directory
from models.fb_campaign_model import FBCampaignProduct, FBCampaignComment, FBCampaignOrder
from api.utilities.api_orm_utilities import *
from api.utilities.api_utilities import *
from api.utilities.fb_api_utilities import *
from api.utilities.localization import *


def update_campaign_order_totals(fb_campaign_id):
    try:
        fb_campaign_id = int(fb_campaign_id)
        # Calculate orders for each product
        fb_campaign_products = orm_get_fb_campaign_products(
            fb_campaign_id)

        for fb_campaign_product in fb_campaign_products:
            # Get the sum of orders of each product
            product_order_amount = get_fb_campaign_product_order_qty_sum(
                fb_campaign_id, fb_campaign_product.product_id)
            if not product_order_amount:
                product_order_amount = 0

            fb_campaign_product.product_order_amount = product_order_amount
            db.session.commit()
    except:
        logger.error(traceback.format_exc())


def check_campaign_product_sold_out(fb_campaign_id):
    try:
        fb_campaign_products = orm_get_fb_campaign_products(fb_campaign_id)

        for fb_campaign_product in fb_campaign_products:
            if fb_campaign_product.product_active_stat == 1:
                if fb_campaign_product.product_quantity <= fb_campaign_product.product_order_amount:
                    setattr(fb_campaign_product, "product_active_stat", 0)
                    db.session.commit()

                    comment_on_campaign_action(
                        fb_campaign_id, fb_campaign_product.order_code, 'sold_out_campaign_product')
    except:
        logger.error(traceback.format_exc())


def get_fb_campaign_product_order_qty_sum(fb_campaign_id, product_id):
    order_qty = db.session.execute(FBCampaignOrder.query.filter_by(
        fb_campaign_id=fb_campaign_id,
        product_id=product_id
    )
        .statement.with_only_columns([func.sum(FBCampaignOrder.order_qty)])).scalar()

    return order_qty


def get_fb_campaign_product_quantity(fb_campaign_id, product_id):
    product_order_quantity = FBCampaignProduct.query.filter(
        FBCampaignProduct.fb_campaign_id == fb_campaign_id,
        FBCampaignProduct.product_id == product_id
    ).with_entities(FBCampaignProduct.product_quantity).first()

    return product_order_quantity[0]


def get_fb_campaign_product_order_amount(fb_campaign_id, product_id):
    product_order_amount = FBCampaignProduct.query.filter(
        FBCampaignProduct.fb_campaign_id == fb_campaign_id,
        FBCampaignProduct.product_id == product_id
    ).with_entities(FBCampaignProduct.product_order_amount).first()

    return product_order_amount[0]


def get_fb_campaign_product_max_order_amount(fb_campaign_id, product_id):
    product_order_max_order_amount = FBCampaignProduct.query.filter(
        FBCampaignProduct.fb_campaign_id == fb_campaign_id,
        FBCampaignProduct.product_id == product_id
    ).with_entities(FBCampaignProduct.max_order_amount).first()

    return product_order_max_order_amount[0]


def get_campaign_total_comment(fb_campaign_id):
    total_commnet = None
    try:
        total_commnet = db.session.execute(FBCampaignComment.query.filter_by(
            fb_campaign_id=int(fb_campaign_id)).statement.
            with_only_columns([func.count()]).order_by(None)).scalar()
    except:
        logger.error(traceback.format_exc())
    return total_commnet


def create_fb_campaign_comment(fb_campaign_id, comment):
    try:
        id = comment["from"]["id"]
    except:
        id = ''
    try:
        name = comment["from"]["name"]
    except:
        name = ''
    try:
        picture_url = comment["from"]["picture"]["data"]["url"]
    except:
        picture_url = ''

    fb_campaign_comment = FBCampaignComment(
        fb_campaign_id=int(fb_campaign_id),
        fb_comment_id=comment["id"],
        fb_user_id=id,
        fb_user_name=name,
        message=comment["message"],
        created_time=comment["created_time"],
        picture_url=picture_url
    )
    return fb_campaign_comment


def get_last_comment_created_time(fb_campaign_id):
    last_comment_created_time = None
    try:
        last_comment_created_time = db.session.query(func.max(FBCampaignComment.created_time)).filter(
            FBCampaignComment.fb_campaign_id == int(fb_campaign_id)).scalar()
    except:
        logger.error(traceback.format_exc())
    if not last_comment_created_time:
        last_comment_created_time = 1

    return last_comment_created_time


def get_last_order_created_time(fb_campaign_id):
    last_order_created_time = None
    try:
        last_order_created_time = db.session.query(
            func.max(FBCampaignOrder.comment_created_time)).filter(
            FBCampaignOrder.fb_campaign_id == int(fb_campaign_id)).scalar()
    except:
        logger.error(traceback.format_exc())
    if not last_order_created_time:
        last_order_created_time = 1

    return last_order_created_time


def get_campaign_order_totals(fb_campaign_id):
    total_campaign_orders = None
    try:
        # Calculate total orders
        total_campaign_orders = db.session.execute(FBCampaignOrder.query.filter_by(
            fb_campaign_id=int(fb_campaign_id)
        )
            .statement.with_only_columns([func.sum(FBCampaignOrder.order_qty)])).scalar()
    except:
        logger.error(traceback.format_exc())
    return total_campaign_orders


def get_fb_campaign_meta_dict(fb_campaign_id):
    try:
        fb_campaign_metas = orm_get_campaign_metas(fb_campaign_id)
        if not fb_campaign_metas:
            return {}
    except:
        logger.error(traceback.format_exc())
        return {}

    fb_campaign_meta_dict = {}
    for fb_campaign_meta in fb_campaign_metas:
        fb_campaign_meta_dict[fb_campaign_meta.meta_key] = fb_campaign_meta.meta_value

    return fb_campaign_meta_dict


def get_order_code_dict(fb_campaign_id):
    # Put all products if products are not specified
    try:
        fb_campaign_products = orm_get_fb_campaign_products(fb_campaign_id)
        if not fb_campaign_products:
            return {}
    except:
        logger.error(traceback.format_exc())
        return {}

    order_code_dict = {}
    for fb_campaign_product in fb_campaign_products:
        order_code_dict[fb_campaign_product.product_id] = {
            "order_code": fb_campaign_product.order_code
        }

    return order_code_dict


def check_fb_campaign_order_validation(fb_campaign_id, product_id, order_qty):
    fb_campaign_product = orm_get_fb_campaign_product(
        fb_campaign_id, product_id)
    if not fb_campaign_product:
        return 'invalid'

    if fb_campaign_product.product_order_amount >= fb_campaign_product.product_quantity:
        return 'invalid_sold_out'

    if fb_campaign_product.product_active_stat != 1:
        return 'invalid'

    if fb_campaign_product.max_order_amount != 0 and order_qty > fb_campaign_product.max_order_amount:
        return 'invalid_exceed_max'

    try:
        # Check if exceed left qty
        product_quantity = get_fb_campaign_product_quantity(
            fb_campaign_id, product_id)
        product_order_amount = get_fb_campaign_product_order_amount(
            fb_campaign_id, product_id)
        if order_qty + product_order_amount <= product_quantity:
            return 'valid'
    except:
        logger.error(traceback.format_exc())
        return 'invalid'
    return "invalid"


def comment_on_campaign_action(fb_campaign_id, order_code, action):
    fb_page = orm_get_fb_page_of_fb_campaign_id(fb_campaign_id)
    if action == 'close_campaign_product':
        react_to_close_campaign_product(fb_page, fb_campaign_id, order_code)
    elif action == 'sold_out_campaign_product':
        react_to_sold_out_campaign_product(fb_page, fb_campaign_id, order_code)


def comment_on_campaign_congrats_lucky_draw_winner(fb_campaign_id, fb_user_id, prize_product_id):
    fb_page = orm_get_fb_page_of_fb_campaign_id(fb_campaign_id)
    fb_campaign_comment = orm_get_fb_campaign_comment_by_fb_user_id(fb_user_id)
    fb_campaign_product = orm_get_product_description(prize_product_id)

    react_to_campaign_congrats_lucky_draw_winner(
        fb_page, fb_campaign_id, fb_campaign_comment, fb_campaign_product)


def capture_comment_keyword_order(fb_campaign_comment, fb_page):
    if check_comment_keyword_order(fb_campaign_comment.message):
        request = f'{shopping_cart_init_url}{fb_campaign_comment.fb_campaign_id}/{fb_campaign_comment.fb_user_id}/init'
        ret = requests_get(request)

        handle_comment_keyword_order(fb_campaign_comment, fb_page)


def handle_comment_keyword_order(fb_campaign_comment, fb_page):
    order = orm_get_order(campaign_id=fb_campaign_comment.fb_campaign_id,
                          fb_user_id=fb_campaign_comment.fb_user_id,
                          order_status='cart')
    if not order:
        return
    order_products = orm_get_order_products(order_id=order.id)
    delivery_charge = get_delivery_charge(order)
    modify_total = get_modify_total(order)

    react_to_buyer_on_comment_keyword_order(
        order, order_products, delivery_charge, modify_total, fb_campaign_comment, fb_page)


def get_delivery_charge(order):
    try:
        delivery_charge = orm_get_order_metas(
            order_id=order.id, meta_key='delivery_charge')[0].meta_value
    except:
        delivery_charge = 0
    return delivery_charge


def get_modify_total(order):
    try:
        modify_total = orm_get_order_metas(
            order_id=order.id, meta_key='modify_total')[0].meta_value
    except:
        modify_total = 0
    return modify_total


def check_comment_keyword_order(message):
    message = message.lower().strip()
    return message == 'order'


def handle_campaign_order_validation(fb_campaign_order, fb_page, action):
    if fb_campaign_order.order_stat == 'valid':
        if action == "create":
            react_to_buyer_on_ordering_create(fb_campaign_order, fb_page)
        elif action == "update":
            react_to_buyer_on_ordering_update(fb_campaign_order, fb_page)


#
# Reaction (Localization)
#


def react_to_close_campaign_product(fb_page, fb_campaign_id, order_code):
    msg = localization_msg_react_to_close_campaign_product(
        order_code, lang=fb_page.lang)
    comment_on_campaign(fb_campaign_id, msg)


def react_to_sold_out_campaign_product(fb_page, fb_campaign_id, order_code):
    msg = localization_msg_react_to_sold_out_campaign_product(
        order_code, lang=fb_page.lang)
    comment_on_campaign(fb_campaign_id, msg)


def react_to_campaign_invalid_order(fb_campaign_comment, order_code, fb_page):
    msg = localization_msg_react_to_campaign_invalid_order(
        order_code, lang=fb_page.lang)
    pm_and_comment_on_fb_campaign_comment(fb_page, fb_campaign_comment, msg)


def react_to_campaign_congrats_lucky_draw_winner(fb_page, fb_campaign_id, fb_campaign_comment, fb_campaign_product):
    msg = localization_msg_react_to_campaign_congrats_lucky_draw_winner(
        fb_campaign_comment, fb_campaign_product, lang=fb_page.lang)
    comment_on_campaign(fb_campaign_id, msg)


def react_to_buyer_on_ordering_create(fb_campaign_order, fb_page):
    pm_msg = f"{localization_msg_react_to_buyer_on_ordering_create_pm(fb_campaign_order, lang=fb_page.lang)}{shopping_cart_url}/{str(fb_campaign_order.fb_campaign_id)}/{fb_campaign_order.fb_user_id}"
    comment_msg = localization_msg_react_to_buyer_on_ordering_create_comment(
        fb_campaign_order, lang=fb_page.lang)
    comment_and_pm_on_fb_campaign_order(
        fb_page, fb_campaign_order, comment_msg, pm_msg)


def react_to_buyer_on_ordering_update(fb_campaign_order, fb_page):
    pm_msg = f"{localization_msg_react_to_buyer_on_ordering_update_pm(fb_campaign_order, lang=fb_page.lang)}{shopping_cart_url}/{str(fb_campaign_order.fb_campaign_id)}/{fb_campaign_order.fb_user_id}"
    comment_msg = localization_msg_react_to_buyer_on_ordering_update_comment(
        fb_campaign_order, lang=fb_page.lang)
    comment_and_pm_on_fb_campaign_order(
        fb_page, fb_campaign_order, comment_msg, pm_msg)


def react_to_buyer_on_comment_keyword_order(order, order_products, delivery_charge, modify_total, fb_campaign_comment, fb_page):
    msg = localization_msg_react_to_buyer_on_comment_keyword_order(
        order, order_products, delivery_charge, modify_total, lang=fb_page.lang)
    pm_on_fb_campaign_comment(fb_page, fb_campaign_comment, msg)


def react_to_campaign_invalid_exceed_max_order(fb_page, fb_campaign_comment, order_code, max_order_amount):
    msg = localization_msg_react_to_campaign_invalid_exceed_max_order(
        order_code, max_order_amount, lang=fb_page.lang)
    pm_and_comment_on_fb_campaign_comment(fb_page, fb_campaign_comment, msg)


def react_to_campaign_invalid_sold_out(fb_page, fb_campaign_comment, order_code):
    msg = localization_msg_react_to_campaign_invalid_sold_out(
        order_code, lang=fb_page.lang)
    pm_and_comment_on_fb_campaign_comment(fb_page, fb_campaign_comment, msg)


def react_to_buyer_on_ordering_canceled(fb_page, fb_campaign_comment, order_code):
    msg = localization_msg_react_to_buyer_on_ordering_canceled(
        order_code, lang=fb_page.lang)
    pm_and_comment_on_fb_campaign_comment(fb_page, fb_campaign_comment, msg)


#
# Threading
#


def comment_on_campaign(fb_campaign_id, msg):
    fb_campaign = orm_get_fb_campaign(fb_campaign_id)
    fb_page = orm_get_fb_page_of_fb_campaign_id(fb_campaign_id)

    try:
        threading.Thread(target=page_comment_on_post, args=(
            fb_page.fb_page_token,
            fb_campaign.fb_post_id, msg)
        ).start()
    except:
        logger.error(traceback.format_exc())


def comment_and_pm_on_fb_campaign_order(fb_page, fb_campaign_order, comment_msg, pm_msg):
    try:
        threading.Thread(target=reply_to_buyer_with_pm_and_comment, args=(
            fb_page.fb_page_token,
            fb_campaign_order.comment_id,
            comment_msg,
            pm_msg
        )).start()
    except:
        logger.error(traceback.format_exc())


def pm_and_comment_on_fb_campaign_comment(fb_page, fb_campaign_comment, msg):
    try:
        threading.Thread(target=reply_to_buyer_with_pm_and_comment, args=(
            fb_page.fb_page_token,
            fb_campaign_comment.fb_comment_id,
            msg,
            msg
        )).start()
    except:
        logger.error(traceback.format_exc())


def pm_on_fb_campaign_comment(fb_page, fb_campaign_comment, msg):
    try:
        threading.Thread(target=reply_to_buyer_on_comment_keyword_order, args=(
            fb_page.fb_page_token,
            fb_campaign_comment.fb_comment_id,
            msg
        )).start()
    except:
        logger.error(traceback.format_exc())


# def react_to_buyer_on_comment_keyword(fb_campaign_comment, msg, fb_page):
#     try:
#         threading.Thread(target=reply_to_buyer_on_comment_keyword, args=(
#             fb_page.fb_page_token,
#             fb_campaign_comment.fb_comment_id,
#             msg
#         )).start()
#     except:
#         logger.error(traceback.format_exc())
