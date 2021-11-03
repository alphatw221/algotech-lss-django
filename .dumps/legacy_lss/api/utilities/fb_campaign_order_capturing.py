from config import db, logger, enable_capture_fb_campaign_order, enable_capture_comment_keyword, enable_cancel_order_on_0
import traceback
from api.utilities.fb_campaign_utilities import *
from api.utilities.api_orm_utilities import *
from models.fb_campaign_model import FBCampaignOrder
from sqlalchemy.exc import IntegrityError


def capture_fb_campaign_comment(fb_campaign):
    fb_page = orm_get_fb_page_of_fb_campaign_id(fb_campaign.fb_campaign_id)
    if not fb_page:
        return {"campaign id": fb_campaign.fb_campaign_id, "error": 'fb_page not found'}
    if not fb_campaign.fb_post_id:
        return {"campaign id": fb_campaign.fb_campaign_id, "error": 'fb_post_id not found'}

    # get comments since last_comment_created_time and check if ret has data
    def _get_fb_comments():
        ret = fb_api_get_comments_since(
            fb_page.fb_page_token,
            fb_campaign.fb_post_id,
            last_comment_created_time
        )  # FIXME use fb_live_video_id instead in the future

        try:
            if not isinstance(ret, dict):
                return ret
            if 'error' in ret:
                error = ret.get('error')
                if error['type'] == 'GraphMethodException':
                    fb_campaign.fb_post_id = ""
                    db.session.commit()
                    return "GraphMethodException"
                elif error['type'] == 'OAuthException':
                    fb_campaign.fb_post_id = ""
                    db.session.commit()
                    return 'OAuthException'
                else:
                    return "FB error"
            comments = ret.get("data", None)
        except:
            logger.error(ret.get('error', None))
            return "error"

        if comments is None:
            update_campaign_product_stat(fb_campaign)
            return ret
        elif comments == []:
            update_campaign_product_stat(fb_campaign)
        return comments

    # init data
    fb_campaign_meta_details = get_fb_campaign_meta_dict(
        fb_campaign.fb_campaign_id)
    product_id_order_code_details = get_order_code_dict(
        fb_campaign.fb_campaign_id)
    last_comment_created_time = get_last_comment_created_time(
        fb_campaign.fb_campaign_id)
    comments_updated = 0

    comments = _get_fb_comments()
    if isinstance(comments, str):
        comments_updated = comments
    elif len(comments) == 1 and comments[0].get('created_time', 0) == last_comment_created_time:
        update_campaign_product_stat(fb_campaign)
    else:
        for comment in comments:
            try:
                fb_campaign_comment = create_fb_campaign_comment(
                    fb_campaign.fb_campaign_id, comment)

                db.session.merge(fb_campaign_comment)
                db.session.commit()  # change to the end of for loop?

                last_comment_created_time = fb_campaign_comment.created_time
                comments_updated += 1

                if enable_capture_comment_keyword:
                    capture_comment_keyword(fb_campaign_comment,
                                            fb_campaign_meta_details, fb_page)
                if enable_capture_fb_campaign_order:
                    capture_fb_campaign_order(fb_campaign, fb_campaign_comment,
                                              product_id_order_code_details, fb_page)
                    update_campaign_product_stat(fb_campaign)
            # TESTING
            except IntegrityError:
                db.session.rollback()
            except:
                db.session.rollback()
                logger.error(traceback.format_exc())

            # time.sleep(5000)
            # comments = _get_comments()

    return {"campaign id": fb_campaign.fb_campaign_id,
            "comments updated": comments_updated,
            "total comments": get_campaign_total_comment(fb_campaign.fb_campaign_id),
            'total campaign orders': get_campaign_order_totals(fb_campaign.fb_campaign_id)}


# TODO
def capture_comment_keyword(fb_campaign_comment, fb_campaign_meta_details, fb_page):
    capture_comment_keyword_order(fb_campaign_comment, fb_page)

    """
    comment = fb_campaign_comment.message.lower()
    delivery_charge_strs = ['free delivery', 'delivery charge', 'delivery fee']
    if fb_campaign_meta_details['is_free_delivery_for_order_above_price'] and any(str in comment for str in delivery_charge_strs):
        msg = f"Delivery charge: {fb_campaign_meta_details['delivery_charge']}. Free delivery for orders above {fb_campaign_meta_details['free_delivery_for_order_above_price']}."
        # react_to_buyer_on_comment_keyword(fb_campaign_comment, msg, fb_page)
        print(msg)
    elif 'delivery' in comment:
        msg = f"Delivery date(s): {fb_campaign_meta_details['delivery_start_date']} - {fb_campaign_meta_details['delivery_end_date']}."
        # react_to_buyer_on_comment_keyword(fb_campaign_comment, msg, fb_page)
        print(msg)
    elif 'pickup' in comment:
        msg = f"Pickup date(s): {fb_campaign_meta_details['pickup_start_date']} - {fb_campaign_meta_details['pickup_end_date']}."
        # react_to_buyer_on_comment_keyword(fb_campaign_comment, msg, fb_page)
        print(msg)
    """


def capture_fb_campaign_order(fb_campaign, fb_campaign_comment, product_id_order_code_details, fb_page):
    # For all product in product list, we check all comments for a match.
    for product_id, order_code_details in product_id_order_code_details.items():
        order_code = order_code_details['order_code']
        # Check if there's any order in this comment.
        order_qty = order_qty_in_comment(
            fb_campaign_comment.message, order_code)

        # If 0 then cancel it, if not 0 then record it.
        if enable_cancel_order_on_0 and order_qty == 0:
            try:
                fb_campaign_order = orm_get_fb_campaign_orders(
                    fb_campaign.fb_campaign_id, product_id, fb_campaign_comment.fb_user_id)
                if not fb_campaign_order:
                    continue

                # Delete the campaign order
                fb_campaign_order.order_qty = 0
                fb_campaign_order.order_stat = 'valid'
                db.session.commit()

                react_to_buyer_on_ordering_canceled(
                    fb_page, fb_campaign_comment, order_code)
            except:
                db.session.rollback()
                logger.error(traceback.format_exc())
        elif order_qty:
            # If the buyer is fb page owner itself, ignore this comment
            if fb_campaign_comment.fb_user_id == fb_campaign.fb_page_id:
                continue

            # If the order is not valid, ignore this comment
            order_stat = check_fb_campaign_order_validation(
                fb_campaign.fb_campaign_id, product_id, order_qty)
            if order_stat != 'valid':
                if order_stat == 'invalid':
                    react_to_campaign_invalid_order(
                        fb_campaign_comment, order_code, fb_page)
                elif order_stat == 'invalid_sold_out':
                    react_to_campaign_invalid_sold_out(
                        fb_page, fb_campaign_comment, order_code)
                elif order_stat == 'invalid_exceed_max':
                    max_order_amount = get_fb_campaign_product_max_order_amount(
                        fb_campaign.fb_campaign_id, product_id)
                    react_to_campaign_invalid_exceed_max_order(
                        fb_page, fb_campaign_comment, order_code, max_order_amount)
                continue

            try:
                # Query to check if the order is existed
                fb_campaign_order = orm_get_fb_campaign_orders(
                    fb_campaign.fb_campaign_id, product_id, fb_campaign_comment.fb_user_id, include_lucky_draw=False)

                # If not create one
                if not fb_campaign_order or fb_campaign_order.order_stat == 'process':
                    # Create new campaign product
                    new_fb_campaign_order = FBCampaignOrder(
                        fb_campaign_id=fb_campaign.fb_campaign_id,
                        product_id=product_id,
                        fb_user_id=fb_campaign_comment.fb_user_id,
                        fb_user_name=fb_campaign_comment.fb_user_name,
                        order_qty=order_qty,
                        order_code=order_code,
                        comment_id=fb_campaign_comment.fb_comment_id,
                        comment_message=fb_campaign_comment.message,
                        comment_created_time=fb_campaign_comment.created_time,
                        order_stat=order_stat
                    )
                    db.session.add(new_fb_campaign_order)

                    # Trigger reaction
                    handle_campaign_order_validation(
                        new_fb_campaign_order, fb_page, "create")

                # If checkout don't let buyer place order
                elif fb_campaign_order.order_stat not in ('valid', 'cart'):
                    continue

                # If the oreder exists but the comment_id is older, update it
                elif fb_campaign_order.comment_id != fb_campaign_comment.fb_comment_id:
                    fb_campaign_order.order_qty = order_qty
                    fb_campaign_order.order_code = order_code
                    fb_campaign_order.comment_id = fb_campaign_comment.fb_comment_id
                    fb_campaign_order.comment_message = fb_campaign_comment.message
                    fb_campaign_order.comment_created_time = fb_campaign_comment.created_time
                    fb_campaign_order.order_stat = order_stat

                    # Trigger reaction
                    handle_campaign_order_validation(
                        fb_campaign_order, fb_page, "update")

                # If the oreder exists and the comment_id is the same, ignore it
            except:
                db.session.rollback()
                logger.error(traceback.format_exc())
    try:
        db.session.commit()
    except:
        db.session.rollback()
        logger.error(traceback.format_exc())


def update_campaign_product_stat(fb_campaign):
    update_campaign_order_totals(fb_campaign.fb_campaign_id)
    check_campaign_product_sold_out(fb_campaign.fb_campaign_id)
