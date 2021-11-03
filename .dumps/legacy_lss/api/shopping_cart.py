from config import db, logger, shopping_cart_init_url
from flask import jsonify, request
import traceback
# Import models from models directory
from models.fb_campaign_model import FBCampaignOrder, FBCampaignOrderSchema
from api.utilities.fb_campaign_order_capturing import update_campaign_product_stat
from api.utilities.api_utilities import utc_now_timestamp
from api.utilities.api_orm_utilities import *
from api.utilities.api_utilities import *

# Remove this after swagger implemented
from config import connex_app


@ connex_app.route("/shopping_cart/<fb_campaign_id>", methods=['POST'])
# @jwt_required
def create_shopping_cart_fb_campaign_order(fb_campaign_id):
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    fb_campaign = orm_get_fb_campaign(fb_campaign_id)
    if not fb_campaign:
        return jsonify({"msg": "fb_campaign not found."}), 400

    fb_user_id = data.get('fb_user_id', None)
    if not fb_user_id:
        return jsonify({"msg": "Bad input data. Need: fb_user_id"}), 400

    fb_user_name = orm_get_fb_campaign_comment_by_fb_user_id(fb_user_id)
    fb_user_name = fb_user_name.fb_user_name if fb_user_name else ''

    response = []

    items = data.get('items', [])
    for item in items:
        product_id = item.get('product_id', None)
        order_qty = item.get('order_qty', None)
        if not product_id:
            response.append({'product_id': product_id,
                             "error": "Bad input data. Need: product_id"})
            continue
        if not order_qty:
            response.append({'product_id': product_id,
                             "error": "Bad input data. Need: order_qty (> 0)"})
            continue
        order_qty = int(order_qty)

        update_campaign_product_stat(fb_campaign)
        fb_campaign_product = orm_get_fb_campaign_product(
            fb_campaign_id, product_id)
        if not fb_campaign_product:
            response.append({'product_id': product_id,
                             "error": "fb_campaign_product not found."})
            continue

        if not fb_campaign_product.product_active_stat:
            response.append({'product_id': product_id,
                             'error': "This prodcut can't be added."})
            continue
        if fb_campaign_product.max_order_amount != 0 and fb_campaign_product.max_order_amount < order_qty:
            response.append(
                {'product_id': product_id, 'error':
                 "Product's quantity exceeds max order amount."})
            continue
        elif fb_campaign_product.product_quantity < fb_campaign_product.product_order_amount + order_qty:
            response.append(
                {'product_id': product_id, 'error':
                 "Product's quantity exceeds inventory quantity."})
            continue
        else:
            fb_campaign_order = orm_create_fb_campaign_order(fb_campaign_id, product_id, fb_user_id, fb_user_name,
                                                             order_qty, f'{fb_campaign_product.order_code}/Cart', 'add_product_from_cart', 'add_product_from_cart',
                                                             utc_now_timestamp(), 'valid')
            fb_campaign_order_schema = FBCampaignOrderSchema()
            response.append(
                fb_campaign_order_schema.dump(fb_campaign_order))
            update_campaign_product_stat(fb_campaign)

    return jsonify(response), 201


@ connex_app.route("/shopping_cart/<fb_campaign_id>/<id>", methods=['PUT'])
# @jwt_required
def update_shopping_cart_fb_campaign_order(fb_campaign_id, id):
    try:
        fb_campaign_order = FBCampaignOrder.query.get(id)
        if not fb_campaign_order:
            return jsonify({"msg": "Campaign order not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    order_qty = int(data.get('order_qty', None))
    if order_qty is None:
        return jsonify({"msg": "Bad input data. Need: order_qty"}), 400

    fb_campaign = orm_get_fb_campaign(fb_campaign_id)
    if not fb_campaign:
        return jsonify({"msg": "fb_campaign not found."}), 400

    update_campaign_product_stat(fb_campaign)
    fb_campaign_product = orm_get_fb_campaign_product(
        fb_campaign_id, fb_campaign_order.product_id)
    if not fb_campaign_product:
        return jsonify({"msg": "fb_campaign_product not found."}), 400

    if not fb_campaign_product.customer_editable:
        return {'msg': "This prodcut can't be edited."}, 418
    if not fb_campaign_product.customer_removable and order_qty == 0:
        return {'msg': "This prodcut can't be removed."}, 418
    elif fb_campaign_product.max_order_amount != 0 and fb_campaign_product.max_order_amount < order_qty:
        return {'msg': "Product's quantity exceeds max order amount."}, 418
    elif fb_campaign_product.product_quantity < fb_campaign_product.product_order_amount - fb_campaign_order.order_qty + order_qty:
        return {'msg': "Product's quantity exceeds inventory quantity."}, 418
    else:
        try:
            fb_campaign_order.order_qty = order_qty
            fb_campaign_order.order_stat = 'valid'
            db.session.commit()
        except:
            logger.error(traceback.format_exc())
            return jsonify({"msg": "DB error."}), 500

        update_campaign_product_stat(fb_campaign)

        fb_campaign_order_schema = FBCampaignOrderSchema()
        return fb_campaign_order_schema.jsonify(fb_campaign_order), 200


@ connex_app.route("/shopping_cart/check_order/<fb_campaign_id>/<fb_user_id>", methods=['PUT'])
# @jwt_required
def update_shopping_cart_check_order(fb_campaign_id, fb_user_id):
    try:
        orders = Order.query.filter(
            Order.campaign_id == fb_campaign_id,
            Order.fb_user_id == fb_user_id,
            Order.order_status == 'cart'
        ).order_by(Order.id.asc()).all()
        if not orders:
            return jsonify({"msg": "Order not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    if len(orders) <= 1:
        return '', 200
    else:
        for order in orders[:len(orders)-1]:
            delete_order_by_order_id(order.id)
        request = f'{shopping_cart_init_url}{fb_campaign_id}/{fb_user_id}/init'
        print(request)
        ret = requests_get(request)
        return '', 200
