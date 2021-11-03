from config import db, logger
from flask import jsonify, request
import traceback
# Import models from models directory
from models.fb_campaign_model import (
    FBCampaignProduct, FBCampaignProductSchema,
)
from api.utilities.api_orm_utilities import *
from api.utilities.api_utilities import *
from api.utilities.fb_api_utilities import *
from api.utilities.fb_campaign_utilities import *

from config import connex_app

#
# FB Campaign Product Active Stat
#


@ connex_app.route("/fb_campaign/product/active_stat/<fb_campaign_id>", methods=['PUT'])
# @jwt_required
def update_fb_campaign_products_active_stat(fb_campaign_id):
    fb_campaign_products = orm_get_fb_campaign_products(
        fb_campaign_id)
    if not fb_campaign_products:
        return jsonify({"msg": "Campaign product not found."}), 404

    # Handles the parameter "active_stat"
    active_stat = request.args.get('active_stat', None)
    if not active_stat:
        return jsonify({"msg": "Bad input data. Need: active_stat"}), 400

    try:
        for fb_campaign_product in fb_campaign_products:
            if active_stat == '0':
                setattr(fb_campaign_product, "product_active_stat", 0)
            elif active_stat == '1':
                setattr(fb_campaign_product, "product_active_stat", 1)
            else:
                return jsonify({"msg": "The active_stat parameter is not supported"}), 400
            db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    return jsonify({'msg': f'number of updates: {len(fb_campaign_products)}'}), 200


@ connex_app.route("/fb_campaign/product/active_stat/<fb_campaign_id>/<product_id>", methods=['PUT'])
# @jwt_required
def update_fb_campaign_product_active_stat(fb_campaign_id, product_id):
    fb_campaign_product = orm_get_fb_campaign_product(
        fb_campaign_id, product_id)
    if not fb_campaign_product:
        return jsonify({"msg": "Campaign product not found."}), 404

    # Handles the parameter "active_stat"
    active_stat = request.args.get('active_stat', None)
    if not active_stat:
        return jsonify({"msg": "Bad input data. Need: active_stat"}), 400

    try:
        if active_stat == '0':
            setattr(fb_campaign_product, "product_active_stat", 0)
            db.session.commit()

            comment_on_campaign_action(
                fb_campaign_id, fb_campaign_product.order_code, 'close_campaign_product')
        elif active_stat == '1':
            setattr(fb_campaign_product, "product_active_stat", 1)
            db.session.commit()
        else:
            return jsonify({"msg": "The active_stat parameter is not supported"}), 400
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_product_schema = FBCampaignProductSchema()
    return fb_campaign_product_schema.jsonify(fb_campaign_product), 200


#
# FB Campaign Product Active
#


@ connex_app.route("/fb_campaign/product/active", methods=['POST'])
# @jwt_required
def create_fb_campaign_product_active():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    fb_user_id = data.get('fb_user_id', None)
    campaign_id = data.get('campaign_id', None)
    campaign_product_id = data.get('campaign_product_id', None)
    if not fb_user_id:
        return jsonify({"msg": "Bad input data. Need: fb_user_id"}), 400
    if not campaign_id:
        return jsonify({"msg": "Bad input data. Need: campaign_id"}), 400
    if not campaign_product_id:
        return jsonify({"msg": "Bad input data. Need: campaign_product_id"}), 400

    fb_campaign_product_active = FBCampaignProductActive(
        fb_user_id=fb_user_id,
        campaign_id=campaign_id,
        campaign_product_id=campaign_product_id,
        user_order_id=data.get('user_order_id', 0),
        fb_page_id=data.get('user_order_id', '')
    )
    db.session.add(fb_campaign_product_active)
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_product_active_schema = FBCampaignProductActiveSchema()
    return fb_campaign_product_active_schema.jsonify(fb_campaign_product_active), 201


@ connex_app.route("/fb_campaign/product/active/<id>", methods=['GET'])
# @jwt_required
def get_fb_campaign_product_active(id):
    fb_campaign_product_active = orm_get_fb_campaign_product_active(id)
    if not fb_campaign_product_active:
        return jsonify({"msg": "FB campaign product active not found."}), 404

    fb_campaign_product_active_schema = FBCampaignProductActiveSchema()
    return fb_campaign_product_active_schema.jsonify(fb_campaign_product_active), 200


@ connex_app.route("/fb_campaign/product/active", methods=['GET'])
# @jwt_required
def get_fb_campaign_product_actives():
    # Handles the parameter: id
    id = request.args.get('id', None)
    if id:
        filter_id = FBCampaignProductActive.id == id
    else:
        filter_id = FBCampaignProductActive.id != None

    # Handles the parameter: fb_user_id
    fb_user_id = request.args.get('fb_user_id', None)
    if fb_user_id:
        filter_fb_user_id = FBCampaignProductActive.fb_user_id == fb_user_id
    else:
        filter_fb_user_id = FBCampaignProductActive.fb_user_id != None

    # Handles the parameter: campaign_id
    campaign_id = request.args.get('campaign_id', None)
    if campaign_id:
        filter_campaign_id = FBCampaignProductActive.campaign_id == campaign_id
    else:
        filter_campaign_id = FBCampaignProductActive.campaign_id != None

    # Handles the parameter: campaign_product_id
    campaign_product_id = request.args.get('campaign_product_id', None)
    if campaign_product_id:
        filter_campaign_product_id = FBCampaignProductActive.campaign_product_id == campaign_product_id
    else:
        filter_campaign_product_id = FBCampaignProductActive.campaign_product_id != None

    # Handles the parameter: user_order_id
    user_order_id = request.args.get('user_order_id', None)
    if user_order_id:
        filter_user_order_id = FBCampaignProductActive.user_order_id == user_order_id
    else:
        filter_user_order_id = FBCampaignProductActive.user_order_id != None

    # Handles the parameter: fb_page_id
    fb_page_id = request.args.get('fb_page_id', None)
    if fb_page_id:
        filter_fb_page_id = FBCampaignProductActive.fb_page_id == fb_page_id
    else:
        filter_fb_page_id = FBCampaignProductActive.fb_page_id != None

    try:
        fb_campaign_product_actives = FBCampaignProductActive.query.filter(
            filter_id,
            filter_fb_user_id,
            filter_campaign_id,
            filter_campaign_product_id,
            filter_user_order_id,
            filter_fb_page_id
        ).all()
        if not fb_campaign_product_actives:
            return jsonify({"msg": "FB campaign product active not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_product_active_schema = FBCampaignProductActiveSchema(
        many=True)
    return fb_campaign_product_active_schema.jsonify(fb_campaign_product_actives), 200


@ connex_app.route("/fb_campaign/product/active/<id>", methods=['PUT'])
# @jwt_required
def update_fb_campaign_product_active(id):
    fb_campaign_product_active = orm_get_fb_campaign_product_active(id)
    if not fb_campaign_product_active:
        return jsonify({"msg": "FB campaign product active not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'id', 'created_at', 'updated_at'}
    # Update each attr name in the given json
    for attr_name, updated_value in data.items():
        # Check for keys that not allowed to update
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            setattr(fb_campaign_product_active, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_product_active_schema = FBCampaignProductActiveSchema()
    return fb_campaign_product_active_schema.jsonify(fb_campaign_product_active), 200


@ connex_app.route("/fb_campaign/product/active/<id>", methods=['DELETE'])
# @jwt_required
def delete_fb_campaign_product_active(id):
    fb_campaign_product_active = orm_get_fb_campaign_product_active(id)
    if not fb_campaign_product_active:
        return jsonify({"msg": "FB campaign product active not found."}), 404

    try:
        db.session.delete(fb_campaign_product_active)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_product_active_schema = FBCampaignProductActiveSchema()
    return fb_campaign_product_active_schema.jsonify(fb_campaign_product_active), 200
