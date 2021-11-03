from config import db, logger
from flask import jsonify, request
import traceback
# Import models from models directory
from models.fb_campaign_model import FBCampaignOrder, FBCampaignOrderSchema
from api.utilities.fb_api_utilities import *
from api.utilities.api_orm_utilities import *

# Remove this after swagger implemented
from config import connex_app


#
# FB Campaign Order
#


@ connex_app.route("/fb_campaign/order/<fb_campaign_id>", methods=['POST'])
# @jwt_required
def create_fb_campaign_order(fb_campaign_id):
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    product_id = data.get('product_id', None)
    fb_user_id = data.get('fb_user_id', None)
    fb_user_name = data.get('fb_user_name', None)
    order_qty = data.get('order_qty', None)
    if not product_id:
        return jsonify({"msg": "Bad input data. Need: product_id"}), 400
    if not fb_user_id:
        return jsonify({"msg": "Bad input data. Need: fb_user_id"}), 400
    if not fb_user_name:
        return jsonify({"msg": "Bad input data. Need: fb_user_name"}), 400
    if not order_qty:
        return jsonify({"msg": "Bad input data. Need: order_qty"}), 400

    # Create new campaign product
    try:
        new_fb_campaign_order = FBCampaignOrder(
            fb_campaign_id=fb_campaign_id,
            product_id=product_id,
            fb_user_id=fb_user_id,
            fb_user_name=fb_user_name,
            order_qty=order_qty,
            order_code=data.get('order_code', ""),
            comment_id=data.get('comment_id', ""),
            comment_message=data.get('comment_message', ""),
            comment_created_time=data.get('comment_created_time', 0),
            order_stat=data.get('order_stat', "")
        )
        db.session.add(new_fb_campaign_order)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_order_schema = FBCampaignOrderSchema()
    return fb_campaign_order_schema.jsonify(new_fb_campaign_order), 201


@ connex_app.route("/fb_campaign/order/<fb_campaign_id>", methods=['GET'])
# @jwt_required
def get_fb_campaign_orders(fb_campaign_id):
    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = FBCampaignOrder.id == id
    else:
        filter_id = FBCampaignOrder.id != None

    # Handles the parameters that filter the order by start_time
    start_time = request.args.get('start_time', -1)
    filter_start_time = FBCampaignOrder.comment_created_time > start_time

    # Handles the parameters that filter the order by end_time
    end_time = request.args.get('end_time', None)
    if not end_time:
        filter_end_time = FBCampaignOrder.comment_created_time != None
    else:
        filter_end_time = FBCampaignOrder.comment_created_time < end_time

    # Handles the parameters that filter the fb_user_id
    fb_user_id = request.args.get('fb_user_id', None)
    if not fb_user_id:
        filter_fb_user_id = FBCampaignOrder.fb_user_id != None
    else:
        filter_fb_user_id = FBCampaignOrder.fb_user_id == fb_user_id

    # Handles the parameters that filter the product_id
    product_id = request.args.get('product_id', None)
    if not product_id:
        filter_product_id = FBCampaignOrder.product_id != None
    else:
        filter_product_id = FBCampaignOrder.product_id == product_id

    # Handles the parameters that filter the comment_id
    comment_id = request.args.get('comment_id', None)
    if not comment_id:
        filter_comment_id = FBCampaignOrder.comment_id != None
    else:
        filter_comment_id = FBCampaignOrder.comment_id == comment_id

    # Handles the parameters that filter the order_stat
    order_stat = request.args.get('order_stat', None)
    if not order_stat:
        filter_order_stat = FBCampaignOrder.order_stat != None
    else:
        filter_order_stat = FBCampaignOrder.order_stat == order_stat

    try:
        fb_campaign_orders = FBCampaignOrder.query.filter(
            FBCampaignOrder.fb_campaign_id == fb_campaign_id,
            filter_id,
            filter_product_id,
            filter_start_time,
            filter_end_time,
            filter_fb_user_id,
            filter_comment_id,
            filter_order_stat
        ).order_by(FBCampaignOrder.comment_created_time.asc()).limit(50).all()
        if not fb_campaign_orders:
            return jsonify({"msg": "Campaign order not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_order_schema = FBCampaignOrderSchema(many=True)
    return fb_campaign_order_schema.jsonify(fb_campaign_orders), 200


@ connex_app.route("/fb_campaign/order/<fb_campaign_id>/<id>", methods=['PUT'])
# @jwt_required
def update_fb_campaign_order(fb_campaign_id, id):
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

    UPDATE_NOT_ALLOWED = {'id', 'fb_campaign_id', 'product_id',
                          'fb_user_id', 'fb_user_name'}
    for attr_name, updated_value in data.items():
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            setattr(fb_campaign_order, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_order_schema = FBCampaignOrderSchema()
    return fb_campaign_order_schema.jsonify(fb_campaign_order), 200


@ connex_app.route("/fb_campaign/order/<fb_campaign_id>", methods=['DELETE'])
# @jwt_required
def delete_fb_campaign_orders(fb_campaign_id):
    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = FBCampaignOrder.id == id
    else:
        filter_id = FBCampaignOrder.id != None

    # Handles the parameters that filter the fb_user_id
    fb_user_id = request.args.get('fb_user_id', None)
    if not fb_user_id:
        filter_fb_user_id = FBCampaignOrder.fb_user_id != None
    else:
        filter_fb_user_id = FBCampaignOrder.fb_user_id == fb_user_id

    # Handles the parameters that filter the product_id
    product_id = request.args.get('product_id', None)
    if not product_id:
        filter_product_id = FBCampaignOrder.product_id != None
    else:
        filter_product_id = FBCampaignOrder.product_id == product_id

    try:
        fb_campaign_orders = FBCampaignOrder.query.filter(
            FBCampaignOrder.fb_campaign_id == fb_campaign_id,
            filter_id,
            filter_fb_user_id,
            filter_product_id
        ).all()
        for fb_campaign_order in fb_campaign_orders:
            db.session.delete(fb_campaign_order)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    return jsonify({"meg": f'Deleteion: {len(fb_campaign_orders)}'}), 200
