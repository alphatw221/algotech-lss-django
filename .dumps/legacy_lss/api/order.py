from config import db, logger
from flask import jsonify, request
import traceback
from models.order_model import (
    Order, OrderSchema,
    OrderMeta, OrderMetaSchema,
    OrderUserMeta, OrderUserMetaSchema,
    OrderProduct, OrderProductSchema,
)
from flask_jwt_extended import jwt_required
from api.utilities.api_orm_utilities import *
from api.utilities.fb_api_utilities import *

# Remove this after swagger implemented
from config import connex_app


#
# Order
#


@ connex_app.route("/order", methods=['POST'])
# @jwt_required
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    new_order = Order(
        campaign_id=data.get('campaign_id', 0),
        customer_id=data.get('customer_id', 0),
        fb_user_id=data.get('fb_user_id', ""),
        fb_user_name=data.get('fb_user_name', ""),
        order_status=data.get('order_status', ""),
        remark=data.get('remark', ""),
        total=data.get('total', 0),
        image=data.get('image', '')
    )
    try:
        db.session.add(new_order)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    order_schema = OrderSchema()
    return order_schema.jsonify(new_order), 201


@ connex_app.route("/order", methods=['GET'])
# @jwt_required
def get_orders():
    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = Order.id == id
    else:
        filter_id = Order.id != None

    # Handles the parameters that filter the order by campaign_id
    campaign_id = request.args.get('campaign_id', None)
    if not campaign_id:
        filter_campaign_id = Order.campaign_id != None
    else:
        filter_campaign_id = Order.campaign_id == campaign_id

    # Handles the parameters that filter the order by customer_id
    customer_id = request.args.get('customer_id', None)
    if not customer_id:
        filter_customer_id = Order.customer_id != None
    else:
        filter_customer_id = Order.customer_id == customer_id

    # Handles the parameters that filter the order by fb_user_id
    fb_user_id = request.args.get('fb_user_id', None)
    if not fb_user_id:
        filter_fb_user_id = Order.fb_user_id != None
    else:
        filter_fb_user_id = Order.fb_user_id == fb_user_id

    # Handles the parameters that filter the start_id
    start_id = request.args.get('start_id', None)
    if not start_id:
        filter_start_id = Order.id != None
    else:
        filter_start_id = Order.id > start_id

    # Handles the parameters that filter the order_status
    order_status = request.args.get('order_status', None)
    if not order_status:
        filter_order_status = Order.order_status != None
    else:
        filter_order_status = Order.order_status == order_status

    try:
        orders = Order.query.filter(
            filter_id,
            filter_campaign_id,
            filter_customer_id,
            filter_fb_user_id,
            filter_start_id,
            filter_order_status
        ).order_by(Order.id.asc()).limit(50).all()
        if not orders:
            return jsonify({"msg": "Order not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    order_schema = OrderSchema(many=True)
    return order_schema.jsonify(orders), 200


@ connex_app.route("/order/<id>", methods=['PUT'])
# @jwt_required
def update_order(id):
    try:
        order = Order.query.get(id)
        if not order:
            return jsonify({"msg": "Order not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'id', 'created_time', 'modified_time'}
    # Update each attr name in the given json
    for attr_name, updated_value in data.items():
        # Check for keys that not allowed to update
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            setattr(order, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    order_schema = OrderSchema()
    return order_schema.jsonify(order), 200


@ connex_app.route("/order/<id>", methods=['DELETE'])
# @jwt_required
def delete_order(id):
    order = delete_order_by_order_id(id)
    return {}, 204


#
# Order Meta
#


@ connex_app.route("/order/meta", methods=['POST', 'PUT'])
# @jwt_required
def update_order_meta():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    order_id = data.get('order_id', None)
    meta_key = data.get('meta_key', None)
    if not order_id:
        return jsonify({"msg": "Bad input data. Need: order_id"}), 400
    if not meta_key:
        return jsonify({"msg": "Bad input data. Need: meta_key"}), 400

    # Check if the order meta is already existed
    try:
        order_meta = OrderMeta.query.filter_by(
            order_id=order_id, meta_key=meta_key).order_by(OrderMeta.id.desc()).first()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    # If existed, update the value
    if order_meta:
        order_meta.meta_value = data.get('meta_value', '')
    else:
        order_meta = OrderMeta(
            order_id=order_id,
            meta_key=meta_key,
            meta_value=data.get('meta_value', "")
        )
        db.session.add(order_meta)

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    order_meta_schema = OrderMetaSchema()
    return order_meta_schema.jsonify(order_meta), 201


@ connex_app.route("/order/meta", methods=['GET'])
# @jwt_required
def get_order_meta():
    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = OrderMeta.id == id
    else:
        filter_id = OrderMeta.id != None

    # Handles the parameters order_id
    order_id = request.args.get('order_id', None)
    if order_id:
        filter_order_id = OrderMeta.order_id == order_id
    else:
        filter_order_id = OrderMeta.order_id != None

    # Handles the parameters meta_key
    meta_key = request.args.get('meta_key', None)
    if meta_key:
        filter_meta_key = OrderMeta.meta_key == meta_key
    else:
        filter_meta_key = OrderMeta.meta_key != None

    # Handles the parameters meta_value
    meta_value = request.args.get('meta_value', None)
    if meta_value:
        filter_meta_value = OrderMeta.meta_value == meta_value
    else:
        filter_meta_value = OrderMeta.meta_value != None

    try:
        order_metas = OrderMeta.query.filter(
            filter_id,
            filter_order_id,
            filter_meta_key,
            filter_meta_value
        ).order_by(OrderMeta.id.asc()).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    # Emtpy query result
    if not order_metas:
        return jsonify({"msg": "Order meta not found."}), 404

    order_meta_schema = OrderMetaSchema(many=True)
    return order_meta_schema.jsonify(order_metas), 200


@ connex_app.route("/order/meta", methods=['DELETE'])
# @jwt_required
def delete_order_meta():
    # Will delete the entire table if no parameters are given
    if len(request.args) == 0:
        return jsonify({"msg": "Parameters needed."}), 400

    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = OrderMeta.id == id
    else:
        filter_id = OrderMeta.id != None

    # Handles the parameters order_id
    order_id = request.args.get('order_id', None)
    if order_id:
        filter_order_id = OrderMeta.order_id == order_id
    else:
        filter_order_id = OrderMeta.order_id != None

    # Handles the parameters meta_key
    meta_key = request.args.get('meta_key', None)
    if meta_key:
        filter_meta_key = OrderMeta.meta_key == meta_key
    else:
        filter_meta_key = OrderMeta.meta_key != None

    # Handles the parameters meta_value
    meta_value = request.args.get('meta_value', None)
    if meta_value:
        filter_meta_value = OrderMeta.meta_value == meta_value
    else:
        filter_meta_value = OrderMeta.meta_value != None

    try:
        order_metas = OrderMeta.query.filter(
            filter_id,
            filter_order_id,
            filter_meta_key,
            filter_meta_value
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    # Emtpy query result
    if not order_metas:
        return jsonify({"msg": "Order meta not found."}), 404

    # Stat for return
    num_of_deletion = len(order_metas)

    try:
        for order_meta in order_metas:
            db.session.delete(order_meta)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    return jsonify({"Number of deletion": num_of_deletion}), 200


#
# Order User Meta
#


@ connex_app.route("/order/user/meta", methods=['POST', 'PUT'])
# @jwt_required
def update_order_user_meta():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    order_id = data.get('order_id', None)
    meta_key = data.get('meta_key', None)
    if not order_id:
        return jsonify({"msg": "Bad input data. Need: order_id"}), 400
    if not meta_key:
        return jsonify({"msg": "Bad input data. Need: meta_key"}), 400

    # Check if the order meta is already existed
    try:
        order_user_meta = OrderUserMeta.query.filter_by(
            order_id=order_id, meta_key=meta_key).order_by(OrderUserMeta.id.desc()).first()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    # If existed, update the value
    if order_user_meta:
        order_user_meta.meta_value = data.get('meta_value', '')

        try:
            db.session.commit()
        except:
            logger.error(traceback.format_exc())
            return jsonify({"msg": "DB error."}), 500
    # If not existed, create a new one
    else:
        try:
            order_user_meta = OrderUserMeta(
                order_id=order_id,
                meta_key=meta_key,
                meta_value=data.get('meta_value', "")
            )
        except:
            logger.error(traceback.format_exc())
            return jsonify({"msg": "DB error."}), 500
        try:
            db.session.add(order_user_meta)
            db.session.commit()
        except:
            logger.error(traceback.format_exc())
            return jsonify({"msg": "DB error."}), 500

    order_meta_schema = OrderUserMetaSchema()
    return order_meta_schema.jsonify(order_user_meta), 201


@ connex_app.route("/order/user/meta", methods=['GET'])
# @jwt_required
def get_order_user_meta():
    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = OrderUserMeta.id == id
    else:
        filter_id = OrderUserMeta.id != None

    # Handles the parameters order_id
    order_id = request.args.get('order_id', None)
    if order_id:
        filter_order_id = OrderUserMeta.order_id == order_id
    else:
        filter_order_id = OrderUserMeta.order_id != None

    # Handles the parameters meta_key
    meta_key = request.args.get('meta_key', None)
    if meta_key:
        filter_meta_key = OrderUserMeta.meta_key == meta_key
    else:
        filter_meta_key = OrderUserMeta.meta_key != None

    # Handles the parameters meta_value
    meta_value = request.args.get('meta_value', None)
    if meta_value:
        filter_meta_value = OrderUserMeta.meta_value == meta_value
    else:
        filter_meta_value = OrderUserMeta.meta_value != None

    try:
        order_user_metas = OrderUserMeta.query.filter(
            filter_id,
            filter_order_id,
            filter_meta_key,
            filter_meta_value
        ).order_by(OrderUserMeta.id.asc()).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    # Emtpy query result
    if not order_user_metas:
        return jsonify({"msg": "Order meta not found."}), 404

    order_meta_schema = OrderUserMetaSchema(many=True)
    return order_meta_schema.jsonify(order_user_metas), 200


@ connex_app.route("/order/user/meta", methods=['DELETE'])
# @jwt_required
def delete_order_user_meta():
    # Will delete the entire table if no parameters are given
    if len(request.args) == 0:
        return jsonify({"msg": "Parameters needed."}), 400

    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = OrderUserMeta.id == id
    else:
        filter_id = OrderUserMeta.id != None

    # Handles the parameters order_id
    order_id = request.args.get('order_id', None)
    if order_id:
        filter_order_id = OrderUserMeta.order_id == order_id
    else:
        filter_order_id = OrderUserMeta.order_id != None

    # Handles the parameters meta_key
    meta_key = request.args.get('meta_key', None)
    if meta_key:
        filter_meta_key = OrderUserMeta.meta_key == meta_key
    else:
        filter_meta_key = OrderUserMeta.meta_key != None

    # Handles the parameters meta_value
    meta_value = request.args.get('meta_value', None)
    if meta_value:
        filter_meta_value = OrderUserMeta.meta_value == meta_value
    else:
        filter_meta_value = OrderUserMeta.meta_value != None

    try:
        order_user_metas = OrderUserMeta.query.filter(
            filter_id,
            filter_order_id,
            filter_meta_key,
            filter_meta_value
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    # Emtpy query result
    if not order_user_metas:
        return jsonify({"msg": "Order meta not found."}), 404

    # Stat for return
    num_of_deletion = len(order_user_metas)

    try:
        for order_meta in order_user_metas:
            db.session.delete(order_meta)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    return jsonify({"Number of deletion": num_of_deletion}), 200


#
# Order Product
#


@ connex_app.route("/order/product", methods=['POST'])
# @jwt_required
def create_order_product():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    order_id = data.get('order_id', None)
    if not order_id:
        return jsonify({"msg": "Bad input data. Need: order_id"}), 400

    try:
        new_order_product = OrderProduct(
            order_id=order_id,
            product_id=data.get('product_id', 0),
            name=data.get('name', ""),
            order_code=data.get('order_code', ""),
            modelname=data.get('modelname', ""),
            quantity=data.get('quantity', 0),
            price=data.get('price', 0),
            total=data.get('total', 0),
            tax=data.get('tax', 0),
            reward=data.get('reward', 0),
            fb_campaign_order_id=data.get('fb_campaign_order_id', 0),
            remark=data.get('remark', "")
        )
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    try:
        db.session.add(new_order_product)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    order_product_schema = OrderProductSchema()
    return order_product_schema.jsonify(new_order_product), 201


@ connex_app.route("/order/product", methods=['GET'])
# @jwt_required
def get_order_products():
    # Will delete the entire table if no parameters are given
    if len(request.args) == 0:
        return jsonify({"msg": "Parameters needed."}), 400

    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = OrderProduct.id == id
    else:
        filter_id = OrderProduct.id != None

    # Handles the parameters order_id
    order_id = request.args.get('order_id', None)
    if order_id:
        filter_order_id = OrderProduct.order_id == order_id
    else:
        filter_order_id = OrderProduct.order_id != None

    # Handles the parameters product_id
    product_id = request.args.get('product_id', None)
    if product_id:
        filter_product_id = OrderProduct.product_id == product_id
    else:
        filter_product_id = OrderProduct.product_id != None

    # Handles the parameters fb_campaign_order_id
    fb_campaign_order_id = request.args.get('fb_campaign_order_id', None)
    if fb_campaign_order_id:
        filter_fb_campaign_order_id = OrderProduct.fb_campaign_order_id == fb_campaign_order_id
    else:
        filter_fb_campaign_order_id = OrderProduct.fb_campaign_order_id != None

    try:
        order_products = OrderProduct.query.filter(
            filter_id,
            filter_order_id,
            filter_product_id,
            filter_fb_campaign_order_id
        ).all()
        if not order_products:
            return jsonify({"msg": "Order product not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    order_product_schema = OrderProductSchema(many=True)
    return order_product_schema.jsonify(order_products), 200


@ connex_app.route("/order/product/<id>", methods=['GET'])
# @jwt_required
def get_order_product(id):
    try:
        order_product = OrderProduct.query.get(id)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    # Emtpy query result
    if not order_product:
        return jsonify({"msg": "Order product not found."}), 404

    order_product_schema = OrderProductSchema()
    return order_product_schema.jsonify(order_product), 200


@ connex_app.route("/order/product/<id>", methods=['PUT'])
# @jwt_required
def update_order_product(id):
    try:
        order_product = OrderProduct.query.get(id)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    # Emtpy query result
    if not order_product:
        return jsonify({"msg": "Order product not found."}), 404

    data = request.get_json()
    # If there's no update data provided
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'id', 'order_id'}
    # Update each attr name in the given json
    for attr_name, updated_value in data.items():
        # Check for keys that not allowed to update
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            setattr(order_product, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())
            return jsonify({"msg": "DB error."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    order_product_schema = OrderProductSchema()
    return order_product_schema.jsonify(order_product), 200


@ connex_app.route("/order/product", methods=['DELETE'])
# @jwt_required
def delete_order_product():
    # Will delete the entire table if no parameters are given
    if len(request.args) == 0:
        return jsonify({"msg": "Parameters needed."}), 400

    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = OrderProduct.id == id
    else:
        filter_id = OrderProduct.id != None

    # Handles the parameters order_id
    order_id = request.args.get('order_id', None)
    if order_id:
        filter_order_id = OrderProduct.order_id == order_id
    else:
        filter_order_id = OrderProduct.order_id != None

    # Handles the parameters product_id
    product_id = request.args.get('product_id', None)
    if product_id:
        filter_product_id = OrderProduct.product_id == product_id
    else:
        filter_product_id = OrderProduct.product_id != None

    try:
        order_products = OrderProduct.query.filter(
            filter_id,
            filter_order_id,
            filter_product_id
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    # Emtpy query result
    if not order_products:
        return jsonify({"msg": "Order product not found."}), 404

    # Stat for return
    num_of_deletion = len(order_products)

    try:
        for order_product in order_products:
            db.session.delete(order_product)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    return jsonify({"Number of deletion": num_of_deletion}), 200


"""
#
# Order Status
#


@ connex_app.route("/order/status/<order_status_id>/<language_id>", methods=['GET'])
# @jwt_required
def get_order_status(order_status_id, language_id):
    try:
        order_status = OrderStatus.query.get(
            {"order_status_id": order_status_id, "language_id": language_id})
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not order_status :
        return jsonify({"msg": "Order status not found."}), 404

    order_status_schema = OrderStatusSchema()
    return order_status_schema.jsonify(order_status), 200
"""
