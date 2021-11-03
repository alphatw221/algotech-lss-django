from config import db, logger
import traceback
# import all models
from models.customer_model import *
from models.fb_app_info_model import *
from models.fb_campaign_model import *
from models.fb_messenger_model import *
from models.fb_page_model import *
from models.order_model import *
from models.plan_model import *
from models.product_model import *
from models.user_model import *
from models.user_plan_model import *


def orm_get_user_access(id):
    try:
        user_access = UserAccess.query.filter_by(id=id).first()
        if not user_access:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return user_access


def orm_get_user_accesses(fb_user_id=None, fb_page_id=None):
    if fb_user_id:
        filter_fb_user_id = UserAccess.fb_user_id == fb_user_id
    else:
        filter_fb_user_id = UserAccess.fb_user_id != None

    if fb_page_id:
        filter_fb_page_id = UserAccess.fb_page_id == fb_page_id
    else:
        filter_fb_page_id = UserAccess.fb_page_id != None

    try:
        user_accesses = UserAccess.query.filter(
            filter_fb_user_id,
            filter_fb_page_id
        ).all()
        if not user_accesses:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return user_accesses


def orm_get_user_plan(id):
    try:
        user_plan = UserPlan.query.filter_by(id=id).first()
        if not user_plan:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return user_plan


def orm_get_user_plans():
    try:
        user_plans = UserPlan.query.all()
        if not user_plans:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return user_plans


def orm_get_user(fb_user_id):
    try:
        user = User.query.filter_by(fb_user_id=fb_user_id).first()
        if not user:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return user


def orm_get_user_order(id):
    try:
        user_order = UserOrder.query.get(id)
        if not user_order:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return user_order


def orm_get_fb_campaign_product_active(id):
    try:
        fb_campaign_product_active = FBCampaignProductActive.query.get(id)
        if not fb_campaign_product_active:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return fb_campaign_product_active


def orm_get_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return product


def orm_get_product_description(product_id, language_id=0):
    try:
        product_description = ProductDescription.query.get(
            {"product_id": product_id, "language_id": language_id})
        if not product_description:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return product_description


def orm_get_product_descriptions_by_list(product_id_list, language_id=0):
    product_description_list = []
    for product_id in product_id_list:
        product_description = orm_get_product_description(
            product_id, language_id)
        product_description_list.append(product_description)

    return product_description_list


def orm_get_product_descriptions_of_campaign(fb_campaign_id):
    fb_campaign_products = orm_get_fb_campaign_products(fb_campaign_id)
    id_list_of_fb_campaign_products = [
        fb_campaign_product.product_id for fb_campaign_product in fb_campaign_products]
    product_descriptions = orm_get_product_descriptions_by_list(
        id_list_of_fb_campaign_products)
    return product_descriptions


def orm_get_fb_page(fb_page_id):
    try:
        fb_page = FBPage.query.filter_by(fb_page_id=fb_page_id).first()
        if not fb_page:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return fb_page


def orm_get_user_fb_page(fb_user_id=None, fb_page_id=None):
    try:
        user_fb_page = UserFBPage.query.filter(
            UserFBPage.fb_user_id == fb_user_id,
            UserFBPage.fb_page_id == fb_page_id
        ).first()
    except:
        logger.error(traceback.format_exc())
        return None

    return user_fb_page


def orm_get_user_metas(fb_user_id=None, meta_key=None, meta_value=None):
    if fb_user_id:
        filter_fb_user_id = UserMeta.fb_user_id == fb_user_id
    else:
        filter_fb_user_id = UserMeta.fb_user_id != None

    if meta_key:
        filter_meta_key = UserMeta.meta_key == meta_key
    else:
        filter_meta_key = UserMeta.meta_key != None

    if meta_value:
        filter_meta_value = UserMeta.meta_value == meta_value
    else:
        filter_meta_value = UserMeta.meta_value != None

    try:
        user_metas = UserMeta.query.filter(
            filter_fb_user_id,
            filter_meta_key,
            filter_meta_value
        ).all()
        if not user_metas:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return user_metas


def orm_get_campaign_metas(fb_campaign_id=None, meta_key=None, meta_value=None):
    if fb_campaign_id:
        filter_fb_campaign_id = CampaignMeta.fb_campaign_id == fb_campaign_id
    else:
        filter_fb_campaign_id = CampaignMeta.fb_campaign_id != None

    if meta_key:
        filter_meta_key = CampaignMeta.meta_key == meta_key
    else:
        filter_meta_key = CampaignMeta.meta_key != None

    if meta_value:
        filter_meta_value = CampaignMeta.meta_value == meta_value
    else:
        filter_meta_value = CampaignMeta.meta_value != None

    try:
        campaign_metas = CampaignMeta.query.filter(
            filter_fb_campaign_id,
            filter_meta_key,
            filter_meta_value
        ).all()
        if not campaign_metas:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return campaign_metas


def orm_get_fb_page_metas(fb_page_id=None, meta_key=None, meta_value=None):
    if fb_page_id:
        filter_fb_page_id = FBPageMeta.fb_page_id == fb_page_id
    else:
        filter_fb_page_id = FBPageMeta.fb_page_id != None

    if meta_key:
        filter_meta_key = FBPageMeta.meta_key == meta_key
    else:
        filter_meta_key = FBPageMeta.meta_key != None

    if meta_value:
        filter_meta_value = FBPageMeta.meta_value == meta_value
    else:
        filter_meta_value = FBPageMeta.meta_value != None

    try:
        user_metas = FBPageMeta.query.filter(
            filter_fb_page_id,
            filter_meta_key,
            filter_meta_value
        ).all()
        if not user_metas:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return user_metas


def orm_get_fb_page_of_fb_campaign_id(fb_campaign_id):
    try:
        fb_campaign = FBCampaign.query.get(fb_campaign_id)
        if not fb_campaign:
            return None

        fb_page = FBPage.query.filter_by(
            fb_page_id=fb_campaign.fb_page_id
        ).first()
    except:
        logger.error(traceback.format_exc())
        return None

    return fb_page


def orm_get_fb_campaign(fb_campaign_id):
    try:
        fb_campaign = FBCampaign.query.get(fb_campaign_id)
        if not fb_campaign:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return fb_campaign


def orm_get_fb_campaigns_by_now(dt_now):
    try:
        fb_campaigns = FBCampaign.query.filter(
            FBCampaign.start_time <= dt_now,
            FBCampaign.end_time >= dt_now,
        ).all()
        if not fb_campaigns:
            return []
    except:
        logger.error(traceback.format_exc())
        return []

    return fb_campaigns


def orm_get_fb_campaigns_by_end_time_delta(dt_now, delta):
    try:
        fb_campaigns = FBCampaign.query.filter(
            FBCampaign.start_time <= dt_now,
            FBCampaign.end_time >= dt_now - delta,
        ).all()
        if not fb_campaigns:
            return []
    except:
        logger.error(traceback.format_exc())
        return None

    return fb_campaigns


def orm_get_fb_campaign_products(fb_campaign_id):
    try:
        fb_campaign_products = FBCampaignProduct.query.filter_by(
            fb_campaign_id=fb_campaign_id).all()
        if not fb_campaign_products:
            return []
    except:
        logger.error(traceback.format_exc())
        return None

    return fb_campaign_products


def orm_get_fb_campaign_product(fb_campaign_id, product_id):
    try:
        fb_campaign_product = FBCampaignProduct.query.get(
            {"fb_campaign_id": fb_campaign_id, "product_id": product_id})
        if not fb_campaign_product:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return fb_campaign_product


def orm_get_product_description(product_id, language_id=0):
    try:
        product_description = ProductDescription.query.get(
            {'product_id': product_id, 'language_id': language_id})
        if not product_description:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return product_description


def orm_get_fb_campaign_comment_by_fb_user_id(fb_user_id):
    try:
        fb_campaign_comment = FBCampaignComment.query.filter_by(
            fb_user_id=fb_user_id).order_by(FBCampaignComment.created_time.desc()).first()
        if not fb_campaign_comment:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return fb_campaign_comment


def orm_get_fb_campaign_order_fb_user_ids(fb_campaign_id, order_stat=None):
    if order_stat:
        filter_order_stat = FBCampaignOrder.order_stat == order_stat
    else:
        filter_order_stat = FBCampaignOrder.order_stat != None

    try:
        fb_campaign_order = FBCampaignOrder.query.filter(
            FBCampaignOrder.fb_campaign_id == fb_campaign_id,
            filter_order_stat,
        ).with_entities(FBCampaignOrder.fb_user_id).distinct().all()
    except:
        logger.error(traceback.format_exc())
        return None

    return fb_campaign_order


def orm_get_fb_campaign_order(id):
    try:
        fb_campaign_order = FBCampaignOrder.query.get(id)
    except:
        logger.error(traceback.format_exc())
        return None

    return fb_campaign_order


def orm_get_fb_campaign_orders(fb_campaign_id, product_id, fb_user_id, include_lucky_draw=True):
    if product_id:
        filter_product_id = FBCampaignOrder.product_id == product_id
    else:
        filter_product_id = FBCampaignOrder.product_id != None

    if include_lucky_draw:
        filter_comment_id = FBCampaignOrder.comment_id != None
    else:
        filter_comment_id = FBCampaignOrder.comment_id != 'lucky_draw'

    try:
        fb_campaign_order = FBCampaignOrder.query.filter(
            FBCampaignOrder.fb_campaign_id == fb_campaign_id,
            filter_product_id,
            filter_comment_id,
            FBCampaignOrder.fb_user_id == fb_user_id).order_by(FBCampaignOrder.id.desc()).first()
    except:
        logger.error(traceback.format_exc())
        return None

    return fb_campaign_order


def orm_create_fb_campaign_order(fb_campaign_id, product_id, fb_user_id, fb_user_name,
                                 order_qty, order_code, comment_id, comment_message,
                                 comment_created_time, order_stat):
    try:
        new_fb_campaign_order = FBCampaignOrder(
            fb_campaign_id=fb_campaign_id,
            product_id=product_id,
            fb_user_id=fb_user_id,
            fb_user_name=fb_user_name,
            order_qty=order_qty,
            order_code=order_code,
            comment_id=comment_id,
            comment_message=comment_message,
            comment_created_time=comment_created_time,
            order_stat=order_stat
        )
        db.session.add(new_fb_campaign_order)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return None

    return new_fb_campaign_order


def orm_create_product_default(fb_user_id, name, description, order_code, price, max_order_amount, quantity, product_type):
    try:
        product = Product(
            fb_user_id=fb_user_id,
            max_order_amount=max_order_amount,
            active_stat=0,
            product_type=product_type,
            remark='',

            modelname=name,
            sku='',
            upc='',
            location='',
            quantity=quantity,
            stock_status_id=0,
            image='',
            manufacturer_id=0,
            shipping=0,
            price=price,
            price_two=0,
            price_three=0,
            points=0,
            date_available=datetime.strptime(
                '1970-01-01T00:00:00', "%Y-%m-%dT%H:%M:%S"),
            height=0,
            subtract=0,
            minimum=0,
            sort_order=0,
            status=0,
            viewed=0
        )
        db.session.add(product)

        db.session.flush()

        product_description = ProductDescription(
            product_id=product.product_id,
            language_id=0,
            name=name,
            description=description,
            tag='',
            order_code=order_code,
            meta_title='',
            meta_description='',
            meta_keyword=''
        )
        db.session.add(product_description)

        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return None

    return product


def orm_create_fb_campaign_product(fb_campaign_id, product_id, order_code, product_quantity, max_order_amount, product_active_stat):
    try:
        fb_campaign_product = FBCampaignProduct(
            fb_campaign_id=fb_campaign_id,
            product_id=product_id,
            order_code=order_code,
            product_quantity=product_quantity,
            product_order_amount=0,
            max_order_amount=max_order_amount,
            product_active_stat=product_active_stat
        )
        db.session.add(fb_campaign_product)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return
    return fb_campaign_product


def orm_get_fb_campaign_stat(fb_campaign_id):
    try:
        fb_campaign_stat = FBCampaignStat.query.get(fb_campaign_id)
        if not fb_campaign_stat:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return fb_campaign_stat


def orm_get_order(campaign_id, fb_user_id, order_status=None):
    try:
        order = Order.query.filter_by(
            campaign_id=campaign_id, fb_user_id=fb_user_id, order_status=order_status).first()
        if not order:
            return None
    except:
        logger.error(traceback.format_exc())
        return None

    return order


def orm_get_orders(campaign_id, order_status=None):
    try:
        orders = Order.query.filter_by(campaign_id=campaign_id)

        if order_status is not None:
            orders = orders.filter_by(order_status=order_status)

        orders = orders.all()
        if not orders:
            return []
    except:
        logger.error(traceback.format_exc())
        return None

    return orders


def orm_get_order_products(order_id=None):
    try:
        order_products = OrderProduct.query.filter(
            OrderProduct.order_id == order_id).all()
        if not order_products:
            return []
    except:
        logger.error(traceback.format_exc())
        return None

    return order_products


def orm_get_order_metas(order_id=None, meta_key=None, meta_value=None):
    if order_id:
        filter_order_id = OrderMeta.order_id == order_id
    else:
        filter_order_id = OrderMeta.order_id != None

    if meta_key:
        filter_meta_key = OrderMeta.meta_key == meta_key
    else:
        filter_meta_key = OrderMeta.meta_key != None

    if meta_value:
        filter_meta_value = OrderMeta.meta_value == meta_value
    else:
        filter_meta_value = OrderMeta.order_id != None

    try:
        order_metas = OrderMeta.query.filter(
            filter_order_id,
            filter_meta_key,
            filter_meta_value
        ).all()
        if not order_metas:
            return []
    except:
        logger.error(traceback.format_exc())
        return None

    return order_metas


def orm_get_order_user_metas(order_id=None, meta_key=None, meta_value=None):
    if order_id:
        filter_order_id = OrderUserMeta.order_id == order_id
    else:
        filter_order_id = OrderUserMeta.order_id != None

    if meta_key:
        filter_meta_key = OrderUserMeta.meta_key == meta_key
    else:
        filter_meta_key = OrderUserMeta.meta_key != None

    if meta_value:
        filter_meta_value = OrderUserMeta.meta_value == meta_value
    else:
        filter_meta_value = OrderUserMeta.order_id != None

    try:
        order_metas = OrderUserMeta.query.filter(
            filter_order_id,
            filter_meta_key,
            filter_meta_value
        ).all()
        if not order_metas:
            return []
    except:
        logger.error(traceback.format_exc())
        return None

    return order_metas


def delete_order_by_order_id(order_id):
    try:
        order_products = orm_get_order_products(order_id=order_id)
        for order_product in order_products:
            fb_campaign_order = orm_get_fb_campaign_order(
                order_product.fb_campaign_order_id)
            fb_campaign_order.order_stat = 'valid'
            db.session.delete(order_product)
        db.session.commit()

        order_metas = orm_get_order_metas(order_id=order_id)
        for order_meta in order_metas:
            db.session.delete(order_meta)
        db.session.commit()

        order_user_metas = orm_get_order_user_metas(order_id=order_id)
        for order_user_meta in order_user_metas:
            db.session.delete(order_user_meta)
        db.session.commit()

        order = Order.query.get(order_id)
        if not order:
            return None
        db.session.delete(order)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())

        return order


def delete_order_all_by_order_id(order_id):
    try:
        order_products = orm_get_order_products(order_id=order_id)
        for order_product in order_products:
            fb_campaign_order = orm_get_fb_campaign_order(
                order_product.fb_campaign_order_id)
            fb_campaign_order.order_stat = 'canceled'
            db.session.delete(order_product)
        db.session.commit()

        order_metas = orm_get_order_metas(order_id=order_id)
        for order_meta in order_metas:
            db.session.delete(order_meta)
        db.session.commit()

        order_user_metas = orm_get_order_user_metas(order_id=order_id)
        for order_user_meta in order_user_metas:
            db.session.delete(order_user_meta)
        db.session.commit()

        order = Order.query.get(order_id)
        if order:
            db.session.delete(order)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())

        return order


# def orm_get_user_group(id):
#     try:
#         user_group = UserGroup.query.filter_by(id=id).first()
#         if not user_group:
#             return None
#     except:
#         logger.error(traceback.format_exc())
#         return None

#     return user_group


# def orm_get_user_groups():
#     try:
#         user_groups = UserGroup.query.all()
#         if not user_groups:
#             return None
#     except:
#         logger.error(traceback.format_exc())
#         return None

#     return user_groups
