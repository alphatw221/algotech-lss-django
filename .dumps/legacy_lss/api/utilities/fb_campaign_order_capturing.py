
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
