from config import db, logger
from flask import jsonify, request
import traceback
# Import models from models directory
from models.fb_campaign_model import FBCampaignProduct, FBCampaignProductSchema
from api.utilities.fb_api_utilities import *
from api.utilities.api_orm_utilities import *

# Remove this after swagger implemented
from config import connex_app


#
# FB Campaign Product
#


@ connex_app.route("/fb_campaign/product/<fb_campaign_id>", methods=['POST'])
# @jwt_required
def create_fb_campaign_product(fb_campaign_id):
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    product_id = data.get('product_id', None)
    if not product_id:
        return jsonify({"msg": "Bad input data. Need: product_id"}), 400

    # Create new campaign product
    try:
        fb_campaign_product = FBCampaignProduct(
            fb_campaign_id=fb_campaign_id,
            product_id=product_id,
            name=data.get('name', ""),
            order_code=data.get('order_code', ""),
            product_type=data.get('product_type', "product"),
            product_quantity=data.get(
                'product_quantity', 0),
            product_order_amount=0,
            max_order_amount=data.get(
                'max_order_amount', 0),
            customer_removable=data.get(
                'customer_removable', False),
            customer_editable=data.get(
                'customer_editable', False),
            product_active_stat=data.get(
                'product_active_stat', 0)
        )
        db.session.add(fb_campaign_product)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_product_schema = FBCampaignProductSchema()
    return fb_campaign_product_schema.jsonify(fb_campaign_product), 201


@ connex_app.route("/fb_campaign/product/<fb_campaign_id>", methods=['GET'])
# @jwt_required
def get_fb_campaign_products(fb_campaign_id):
    # Handles the parameter: product_id
    product_id = request.args.get('product_id', None)
    if product_id:
        filter_product_id = FBCampaignProduct.product_id == product_id
    else:
        filter_product_id = FBCampaignProduct.product_id != None

    # Handles the parameter: product_active_stat
    product_active_stat = request.args.get('product_active_stat', None)
    if product_active_stat:
        filter_product_active_stat = FBCampaignProduct.product_active_stat == product_active_stat
    else:
        filter_product_active_stat = FBCampaignProduct.product_active_stat != None

    # Handles the parameter: order_code
    order_code = request.args.get('order_code', None)
    if order_code:
        filter_order_code = FBCampaignProduct.order_code == order_code
    else:
        filter_order_code = FBCampaignProduct.order_code != None

    # Handles the parameter: customer_removable
    customer_removable = request.args.get('customer_removable', None)
    if customer_removable:
        filter_customer_removable = FBCampaignProduct.customer_removable == customer_removable
    else:
        filter_customer_removable = FBCampaignProduct.customer_removable != None

    # Handles the parameter: customer_editable
    customer_editable = request.args.get('customer_editable', None)
    if customer_editable:
        filter_customer_editable = FBCampaignProduct.customer_editable == customer_editable
    else:
        filter_customer_editable = FBCampaignProduct.customer_editable != None

    try:
        fb_campaign_products = FBCampaignProduct.query.filter(
            FBCampaignProduct.fb_campaign_id == fb_campaign_id,
            filter_product_id,
            filter_product_active_stat,
            filter_order_code,
            filter_customer_removable,
            filter_customer_editable
        ).all()
        if not fb_campaign_products:
            return jsonify({"msg": "Campaign product not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_product_schema = FBCampaignProductSchema(many=True)
    return fb_campaign_product_schema.jsonify(fb_campaign_products), 200


@ connex_app.route("/fb_campaign/product/<fb_campaign_id>/<product_id>", methods=['GET'])
# @jwt_required
def get_fb_campaign_product(fb_campaign_id, product_id):
    try:
        fb_campaign_product = FBCampaignProduct.query.get(
            {"fb_campaign_id": fb_campaign_id, "product_id": product_id})
        if not fb_campaign_product:
            return jsonify({"msg": "Campaign product not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_product_schema = FBCampaignProductSchema()
    return fb_campaign_product_schema.jsonify(fb_campaign_product), 200


@ connex_app.route("/fb_campaign/product/<fb_campaign_id>/<product_id>", methods=['PUT'])
# @jwt_required
def update_fb_campaign_product(fb_campaign_id, product_id):
    try:
        fb_campaign_product = FBCampaignProduct.query.get(
            {"fb_campaign_id": fb_campaign_id, "product_id": product_id})
        if not fb_campaign_product:
            return jsonify({"msg": "Campaign product not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'fb_campaign_id',
                          'product_id', 'product_order_amount'}
    for attr_name, updated_value in data.items():
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            setattr(fb_campaign_product, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_product_schema = FBCampaignProductSchema()
    return fb_campaign_product_schema.jsonify(fb_campaign_product), 200


@ connex_app.route("/fb_campaign/product/<fb_campaign_id>/<product_id>", methods=['DELETE'])
# @jwt_required
def delete_fb_campaign_product(fb_campaign_id, product_id):
    try:
        fb_campaign_product = FBCampaignProduct.query.get(
            {"fb_campaign_id": fb_campaign_id, "product_id": product_id})
        if not fb_campaign_product:
            return jsonify({"msg": "Campaign product not found."}), 404
        db.session.delete(fb_campaign_product)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_product_schema = FBCampaignProductSchema()
    return fb_campaign_product_schema.jsonify(fb_campaign_product), 200


@ connex_app.route("/fb_campaign/product/<fb_campaign_id>", methods=['DELETE'])
# @jwt_required
def delete_fb_campaign_products(fb_campaign_id):
    fb_campaign_products = orm_get_fb_campaign_products(fb_campaign_id)
    if not fb_campaign_products:
        return jsonify({"msg": "Campaign product not found."}), 404
    try:
        FBCampaignProduct.query.filter_by(
            fb_campaign_id=fb_campaign_id).delete()
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    return jsonify({'msg': f'deletion: {len(fb_campaign_products)}'}), 200
