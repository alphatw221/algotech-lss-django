from config import db, logger
from flask import json, jsonify, request
from datetime import datetime
import traceback
from api.utilities.fb_api_utilities import *
from api.utilities.api_orm_utilities import *


# Remove this after swagger implemented
from config import connex_app


#
# User Access
#


@ connex_app.route("/user_access", methods=['POST'])
# @jwt_required
def create_user_access():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    user_access = UserAccess(
        fb_user_id=data.get('fb_user_id', ''),
        fb_page_id=data.get('fb_page_id', ''),
        type=data.get('type', ''),
        start_date=datetime.strptime(
            data.get('created_at', "2020-01-01T00:00:00"), "%Y-%m-%dT%H:%M:%S"),
        end_date=datetime.strptime(
            data.get('created_at', "2020-01-01T00:00:00"), "%Y-%m-%dT%H:%M:%S"),
        remark=data.get('remark', ''),
    )
    try:
        db.session.add(user_access)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_access_schema = UserAccessSchema()
    return user_access_schema.jsonify(user_access), 200


@ connex_app.route("/user_access/<id>", methods=['GET'])
# @jwt_required
def get_user_access(id):
    user_access = orm_get_user_access(id)
    if not user_access:
        return jsonify({"msg": "User access not found."}), 404

    user_access_schema = UserAccessSchema()
    return user_access_schema.jsonify(user_access), 200


@ connex_app.route("/user_access", methods=['GET'])
# @jwt_required
def get_user_accesses():
    fb_user_id = request.args.get('fb_user_id', None)
    fb_page_id = request.args.get('fb_page_id', None)

    user_accesses = orm_get_user_accesses(fb_user_id, fb_page_id)
    if not user_accesses:
        return jsonify({"msg": "User access not found."}), 404

    user_access_schema = UserAccessSchema(many=True)
    return user_access_schema.jsonify(user_accesses), 200


@ connex_app.route("/user_access/<id>", methods=['PUT'])
# @jwt_required
def update_user_access(id):
    user_access = orm_get_user_access(id)
    if not user_access:
        return jsonify({"msg": "User access not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'id'}
    for attr_name, updated_value in data.items():
        if attr_name in UPDATE_NOT_ALLOWED:
            continue
        try:
            setattr(user_access, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_access_schema = UserAccessSchema()
    return user_access_schema.jsonify(user_access), 200


@ connex_app.route("/user_access/<id>", methods=['DELETE'])
# @jwt_required
def delete_user_access(id):
    user_access = orm_get_user_access(id)
    if not user_access:
        return jsonify({"msg": "User access not found."}), 404

    try:
        db.session.delete(user_access)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_access_schema = UserAccessSchema()
    return user_access_schema.jsonify(user_access), 200
