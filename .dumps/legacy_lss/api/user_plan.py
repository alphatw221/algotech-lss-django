from config import db, logger
from flask import json, jsonify, request
from datetime import datetime
import traceback
from api.utilities.fb_api_utilities import *
from api.utilities.api_orm_utilities import *


# Remove this after swagger implemented
from config import connex_app


#
# User Plan
#


@ connex_app.route("/user_plan", methods=['POST'])
# @jwt_required
def create_user_plan():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    user_plan = UserPlan(
        title=data.get('title', ''),
        excerpt=data.get('excerpt', ''),
        content=data.get('content', ''),
        remark=data.get('remark', ''),
        days=data.get('days', 0),
        limit_fb_pages=data.get('limit_fb_pages', 0),
        points=data.get('points', 0),
        status=data.get('status', ''),
        price=data.get('price', 0),
        price_ori=data.get('price_ori', 0),
        image=data.get('image', ''),
        sort_order=data.get('sort_order', 0)
    )
    try:
        db.session.add(user_plan)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_plan_schema = UserPlanSchema()
    return user_plan_schema.jsonify(user_plan), 200


@ connex_app.route("/user_plan/<id>", methods=['GET'])
# @jwt_required
def get_user_plan(id):
    user_plan = orm_get_user_plan(id)
    if not user_plan:
        return jsonify({"msg": "User plan not found."}), 404

    user_plan_schema = UserPlanSchema()
    return user_plan_schema.jsonify(user_plan), 200


@ connex_app.route("/user_plan", methods=['GET'])
# @jwt_required
def get_user_plans():
    user_plans = orm_get_user_plans()
    if not user_plans:
        return jsonify({"msg": "User plan not found."}), 404

    user_plan_schema = UserPlanSchema(many=True)
    return user_plan_schema.jsonify(user_plans), 200


@ connex_app.route("/user_plan/<id>", methods=['PUT'])
# @jwt_required
def update_user_plan(id):
    user_plan = orm_get_user_plan(id)
    if not user_plan:
        return jsonify({"msg": "User plan not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'id', 'created_at', 'updated_at'}
    for attr_name, updated_value in data.items():
        if attr_name in UPDATE_NOT_ALLOWED:
            continue
        try:
            setattr(user_plan, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_plan_schema = UserPlanSchema()
    return user_plan_schema.jsonify(user_plan), 200


@ connex_app.route("/user_plan/<id>", methods=['DELETE'])
# @jwt_required
def delete_user_plan(id):
    user_plan = orm_get_user_plan(id)
    if not user_plan:
        return jsonify({"msg": "User plan not found."}), 404

    try:
        db.session.delete(user_plan)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_plan_schema = UserPlanSchema()
    return user_plan_schema.jsonify(user_plan), 200


#
# User Order
#


@ connex_app.route("/user_order", methods=['POST'])
# @jwt_required
def create_user_order():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    fb_user_id = data.get('fb_user_id', None)
    fb_user_email = data.get('fb_user_email', None)
    if not fb_user_id:
        return jsonify({"msg": "Bad input data. Need: fb_user_id"}), 400
    if not fb_user_email:
        return jsonify({"msg": "Bad input data. Need: fb_user_email"}), 400

    user_order = UserOrder(
        fb_user_id=fb_user_id,
        fb_user_email=fb_user_email,
        created_at=datetime.strptime(
            data.get('created_at', "2020-01-01T00:00:00"), "%Y-%m-%dT%H:%M:%S"),
        updated_at=datetime.strptime(
            data.get('updated_at', "2020-01-01T00:00:00"), "%Y-%m-%dT%H:%M:%S"),
        closed_at=datetime.strptime(
            data.get('closed_at', "2020-01-01T00:00:00"), "%Y-%m-%dT%H:%M:%S"),
        plan_id=data.get('plan_id', 0),
        days=data.get('days', 0),
        limit_fb_pages=data.get('limit_fb_pages', 0),
        points=data.get('points', 0),
        points_left=data.get('points_left', 0),
    )
    db.session.add(user_order)
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_order_schema = UserOrderSchema()
    return user_order_schema.jsonify(user_order), 201


@ connex_app.route("/user_order/<id>", methods=['GET'])
# @jwt_required
def get_user_order(id):
    user_order = orm_get_user_order(id)
    if not user_order:
        return jsonify({"msg": "User order not found."}), 404

    user_order_schema = UserOrderSchema()
    return user_order_schema.jsonify(user_order), 200


@ connex_app.route("/user_order", methods=['GET'])
# @jwt_required
def get_user_orders():
    # Handles the parameter: id
    id = request.args.get('id', None)
    if id:
        filter_id = UserOrder.id == id
    else:
        filter_id = UserOrder.id != None

    # Handles the parameter: fb_user_id
    fb_user_id = request.args.get('fb_user_id', None)
    if fb_user_id:
        filter_fb_user_id = UserOrder.fb_user_id == fb_user_id
    else:
        filter_fb_user_id = UserOrder.fb_user_id != None

    # Handles the parameter: fb_user_email
    fb_user_email = request.args.get('fb_user_email', None)
    if fb_user_email:
        filter_fb_user_email = UserOrder.fb_user_email == fb_user_email
    else:
        filter_fb_user_email = UserOrder.fb_user_email != None

    # Handles the parameter: plan_id
    plan_id = request.args.get('plan_id', None)
    if plan_id:
        filter_plan_id = UserOrder.plan_id == plan_id
    else:
        filter_plan_id = UserOrder.plan_id != None

    try:
        user_orders = UserOrder.query.filter(
            filter_id,
            filter_fb_user_id,
            filter_fb_user_email,
            filter_plan_id,
        ).all()
        if not user_orders:
            return jsonify({"msg": "User order not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_order_schema = UserOrderSchema(many=True)
    return user_order_schema.jsonify(user_orders), 200


@ connex_app.route("/user_order/<id>", methods=['PUT'])
# @jwt_required
def update_user_order(id):
    user_order = orm_get_user_order(id)
    if not user_order:
        return jsonify({"msg": "User order not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'id'}
    # Update each attr name in the given json
    for attr_name, updated_value in data.items():
        # Check for keys that not allowed to update
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            if attr_name == "created_at":
                user_order.created_at = datetime.strptime(
                    data['created_at'], "%Y-%m-%dT%H:%M:%S")
            elif attr_name == "updated_at":
                user_order.updated_at = datetime.strptime(
                    data['updated_at'], "%Y-%m-%dT%H:%M:%S")
            elif attr_name == "closed_at":
                user_order.closed_at = datetime.strptime(
                    data['closed_at'], "%Y-%m-%dT%H:%M:%S")
            else:
                setattr(user_order, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_order_schema = UserOrderSchema()
    return user_order_schema.jsonify(user_order), 200


@ connex_app.route("/user_order/<id>", methods=['DELETE'])
# @jwt_required
def delete_user_order(id):
    user_order = orm_get_user_order(id)
    if not user_order:
        return jsonify({"msg": "User order not found."}), 404

    try:
        db.session.delete(user_order)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_order_schema = UserOrderSchema()
    return user_order_schema.jsonify(user_order), 200


#
# User Order Meta
#


@ connex_app.route("/user_order/meta", methods=['POST', 'PUT'])
# @jwt_required
def update_user_order_meta():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    user_order_id = data.get('user_order_id', None)
    meta_key = data.get('meta_key', None)
    if not user_order_id:
        return jsonify({"msg": "Bad input data. Need: user_order_id"}), 400
    if not meta_key:
        return jsonify({"msg": "Bad input data. Need: meta_key"}), 400

    # Check if the order meta is already existed
    try:
        user_order_meta = UserOrderMeta.query.filter_by(
            user_order_id=user_order_id, meta_key=meta_key).first()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    # If existed, update the value
    if user_order_meta:
        user_order_meta.meta_value = data.get('meta_value', '')
    else:
        user_order_meta = UserOrderMeta(
            user_order_id=user_order_id,
            meta_key=meta_key,
            meta_value=data.get('meta_value', "")
        )
        db.session.add(user_order_meta)

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_order_meta_schema = UserOrderMetaSchema()
    return user_order_meta_schema.jsonify(user_order_meta), 201


@ connex_app.route("/user_order/meta", methods=['GET'])
# @jwt_required
def get_user_order_meta():
    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = UserOrderMeta.id == id
    else:
        filter_id = UserOrderMeta.id != None

    # Handles the parameters user_order_id
    user_order_id = request.args.get('user_order_id', None)
    if user_order_id:
        filter_user_order_id = UserOrderMeta.user_order_id == user_order_id
    else:
        filter_user_order_id = UserOrderMeta.user_order_id != None

    # Handles the parameters meta_key
    meta_key = request.args.get('meta_key', None)
    if meta_key:
        filter_meta_key = UserOrderMeta.meta_key == meta_key
    else:
        filter_meta_key = UserOrderMeta.meta_key != None

    # Handles the parameters meta_value
    meta_value = request.args.get('meta_value', None)
    if meta_value:
        filter_meta_value = UserOrderMeta.meta_value == meta_value
    else:
        filter_meta_value = UserOrderMeta.meta_value != None

    try:
        user_order_metas = UserOrderMeta.query.filter(
            filter_id,
            filter_user_order_id,
            filter_meta_key,
            filter_meta_value
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    # Emtpy query result
    if not user_order_metas:
        return jsonify({"msg": "User Order meta not found."}), 404

    user_order_meta_schema = UserOrderMetaSchema(many=True)
    return user_order_meta_schema.jsonify(user_order_metas), 200


@ connex_app.route("/user_order/meta", methods=['DELETE'])
# @jwt_required
def delete_user_order_meta():
    # Will delete the entire table if no parameters are given
    if len(request.args) == 0:
        return jsonify({"msg": "Parameters needed."}), 400

    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = UserOrderMeta.id == id
    else:
        filter_id = UserOrderMeta.id != None

    # Handles the parameters user_order_id
    user_order_id = request.args.get('user_order_id', None)
    if user_order_id:
        filter_user_order_id = UserOrderMeta.user_order_id == user_order_id
    else:
        filter_user_order_id = UserOrderMeta.user_order_id != None

    # Handles the parameters meta_key
    meta_key = request.args.get('meta_key', None)
    if meta_key:
        filter_meta_key = UserOrderMeta.meta_key == meta_key
    else:
        filter_meta_key = UserOrderMeta.meta_key != None

    # Handles the parameters meta_value
    meta_value = request.args.get('meta_value', None)
    if meta_value:
        filter_meta_value = UserOrderMeta.meta_value == meta_value
    else:
        filter_meta_value = UserOrderMeta.meta_value != None

    try:
        user_order_metas = UserOrderMeta.query.filter(
            filter_id,
            filter_user_order_id,
            filter_meta_key,
            filter_meta_value
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    # Emtpy query result
    if not user_order_metas:
        return jsonify({"msg": "User Order meta not found."}), 404

    # Stat for return
    num_of_deletion = len(user_order_metas)

    try:
        for user_order_meta in user_order_metas:
            db.session.delete(user_order_meta)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    return jsonify({"Number of deletion": num_of_deletion}), 200
