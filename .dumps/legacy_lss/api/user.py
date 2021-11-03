
from config import db, logger
from flask import jsonify, request
import traceback
# Import models from models directory
from models.user_model import User, UserSchema, UserMeta, UserMetaSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.utilities.api_orm_utilities import *
from api.utilities.api_utilities import *
from api.utilities.fb_api_utilities import *

# Remove this after swagger implemented
from config import connex_app


#
# User
#


@ connex_app.route("/user/<fb_user_id>", methods=['POST'])
# @jwt_required
def create_user(fb_user_id):
    if not fb_user_id:
        return jsonify({"msg": "Bad input data. Need: fb_user_id"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    fb_user_email = data.get('fb_user_email', None)
    fb_user_name = data.get('fb_user_name', None)
    if not fb_user_email:
        return jsonify({"msg": "Bad input data. Need: fb_user_email"}), 400
    if not fb_user_name:
        return jsonify({"msg": "Bad input data. Need: fb_user_name"}), 400

    user = orm_get_user(fb_user_id)
    if user:
        # required
        user.fb_user_email = fb_user_email
        user.fb_user_name = fb_user_name
        # optional
        user.fb_user_token = data.get('fb_user_token', None)
        user.company_name = data.get('company_name', None)
        user.phone_number = data.get('phone_number', None)
        user.image = data.get('image', None)
        user.ip = data.get('ip', None)
        user.status = data.get('status', None)
    else:
        user = User(
            # required
            fb_user_id=fb_user_id,
            fb_user_email=fb_user_email,
            fb_user_name=fb_user_name,
            # optional
            fb_user_token=data.get('fb_user_token', ''),
            company_name=data.get('company_name', ''),
            phone_number=data.get('phone_number', ''),
            image=data.get('image', ''),
            ip=data.get('ip', ''),
            status=data.get('status', ''),
        )
        db.session.add(user)
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_schema = UserSchema()
    return user_schema.jsonify(user), 201


@ connex_app.route("/user/<fb_user_id>", methods=['GET'])
# @jwt_required
def get_user(fb_user_id):
    user = orm_get_user(fb_user_id)
    if not user:
        return jsonify({"msg": "User not found."}), 404

    user_schema = UserSchema()
    return user_schema.jsonify(user), 200


@ connex_app.route("/user/<fb_user_id>", methods=['PUT'])
# @jwt_required
def update_user(fb_user_id):
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    user = orm_get_user(fb_user_id)
    if not user:
        return jsonify({"msg": "User not found."}), 404

    UPDATE_NOT_ALLOWED = {'id', 'fb_user_id', 'date_added', 'update_time'}
    for attr_name, updated_value in data.items():
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            setattr(user, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_schema = UserSchema()
    return user_schema.jsonify(user), 200


@ connex_app.route("/user/<fb_user_id>", methods=['DELETE'])
# @jwt_required
def delete_user(fb_user_id):
    user = orm_get_user(fb_user_id)
    if not user:
        return jsonify({"msg": "FB User ID not found."}), 404

    db.session.delete(user)

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_schema = UserSchema()
    return user_schema.jsonify(user), 200


@ connex_app.route("/user/long/<fb_user_id>", methods=['PUT'])
# @jwt_required
def update_user_token_long(fb_user_id):
    user = orm_get_user(fb_user_id)
    if not user:
        return jsonify({"msg": "User not found."}), 404

    long_lived_token = get_long_lived_token_from_short_lived_token(
        user.fb_user_token)
    if not long_lived_token:
        return jsonify({"msg": "FB API failed."}), 500

    try:
        user.fb_user_token = long_lived_token["access_token"]
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "FB API failed."}), 500

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_user_schema = UserSchema()
    return fb_user_schema.jsonify(user), 200


#
# User Meta
#


@ connex_app.route("/user/meta/<fb_user_id>", methods=['POST', 'PUT'])
# @jwt_required
def update_user_meta(fb_user_id):
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    meta_key = data.get('meta_key', None)
    if not meta_key:
        return jsonify({"msg": "Bad input data. Need: meta_key"}), 400
    meta_value = data.get('meta_value', '')
    if not meta_value:
        meta_value = ''

    user_metas = orm_get_user_metas(fb_user_id=fb_user_id, meta_key=meta_key)
    if not user_metas:
        user_meta = UserMeta(
            fb_user_id=fb_user_id,
            meta_key=meta_key,
            meta_value=meta_value
        )
        db.session.add(user_meta)
    else:
        user_meta = next(iter(user_metas))
        user_meta.meta_value = meta_value

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_meta_schema = UserMetaSchema()
    return user_meta_schema.jsonify(user_meta), 201


@ connex_app.route("/user/meta/<fb_user_id>", methods=['GET'])
# @jwt_required
def get_user_metas(fb_user_id):
    meta_key = request.args.get('meta_key', None)
    meta_value = request.args.get('meta_value', None)

    user_metas = orm_get_user_metas(fb_user_id, meta_key, meta_value)
    if not user_metas:
        return jsonify({"msg": "User meta not found."}), 404

    user_meta_schema = UserMetaSchema(many=True)
    return user_meta_schema.jsonify(user_metas), 200


@ connex_app.route("/user/meta/<fb_user_id>", methods=['DELETE'])
# @jwt_required
def delete_user_meta(fb_user_id):
    meta_key = request.args.get('meta_key', None)
    meta_value = request.args.get('meta_value', None)

    user_metas = orm_get_user_metas(fb_user_id, meta_key, meta_value)
    if not user_metas:
        return jsonify({"msg": "User meta not found."}), 404

    try:
        for user_meta in user_metas:
            db.session.delete(user_meta)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    return jsonify({"msg": f'Deletion: {len(user_metas)}'}), 200
