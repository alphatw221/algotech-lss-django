from config import logger
from flask import jsonify, request
from models.fb_page_model import FBPage, FBPageMeta, FBPageMetaSchema, FBPageSchema
from api.utilities.api_orm_utilities import *
from api.utilities.fb_api_utilities import *

# Remove this after swagger implemented
from config import connex_app


@ connex_app.route("/fb_page/<fb_page_id>", methods=['POST', 'PUT'])
# @jwt_required
def create_fb_page(fb_page_id):
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    fb_page_token = data.get('fb_page_token', None)
    fb_page_token_updated_user = data.get('fb_page_token_updated_user', None)
    if not fb_page_token:
        return jsonify({"msg": "Bad input data. Need: fb_page_token"}), 400
    if not fb_page_token_updated_user:
        return jsonify({"msg": "Bad input data. Need: fb_page_token_updated_user"}), 400

    fb_page = orm_get_fb_page(fb_page_id)
    if fb_page:
        fb_page.fb_page_token = fb_page_token
        fb_page.fb_page_token_updated_user = fb_page_token_updated_user
        # optional
        fb_page.fb_page_name = data.get('fb_page_name', None)
        fb_page.fb_page_token_expires_in = data.get(
            'fb_page_token_expires_in', None)
    else:
        fb_page = FBPage(
            fb_page_id=fb_page_id,
            fb_page_token=fb_page_token,
            fb_page_token_updated_user=fb_page_token_updated_user,
            # optional
            fb_page_name=data.get('fb_page_name', ''),
            fb_page_token_expires_in=data.get('fb_page_token_expires_in', 0)
        )
        db.session.add(fb_page)

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_page_schema = FBPageSchema()
    return fb_page_schema.jsonify(fb_page), 201


@ connex_app.route("/fb_page/<fb_page_id>", methods=['GET'])
# @jwt_required
def get_fb_page(fb_page_id):
    fb_page = orm_get_fb_page(fb_page_id)
    if not fb_page:
        return jsonify({"msg": "FB Page not found."}), 404

    fb_page_schema = FBPageSchema()
    return fb_page_schema.jsonify(fb_page), 200


@ connex_app.route("/fb_page/long/<fb_page_id>", methods=['PUT'])
# @jwt_required
def update_fb_page_token_long(fb_page_id):
    fb_page = orm_get_fb_page(fb_page_id)
    if not fb_page:
        return jsonify({"msg": "FB Page not found."}), 404

    long_lived_token = get_long_lived_token_from_short_lived_token(
        fb_page.fb_page_token)
    if not long_lived_token:
        return jsonify({"msg": "FB API failed."}), 500

    try:
        fb_page.fb_page_token = long_lived_token["access_token"]
        fb_page.fb_page_token_expires_in = long_lived_token.get(
            'expires_in', None)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "FB API failed."}), 500

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_page_schema = FBPageSchema()
    return fb_page_schema.jsonify(fb_page), 200


#
# Page Meta
#


@ connex_app.route("/fb_page/meta/<fb_page_id>", methods=['POST', 'PUT'])
# @jwt_required
def update_fb_page_meta(fb_page_id):
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

    fb_page_metas = orm_get_fb_page_metas(
        fb_page_id=fb_page_id, meta_key=meta_key)
    if not fb_page_metas:
        fb_page_meta = FBPageMeta(
            fb_page_id=fb_page_id,
            meta_key=meta_key,
            meta_value=meta_value
        )
        db.session.add(fb_page_meta)
    else:
        fb_page_meta = next(iter(fb_page_metas))
        fb_page_meta.meta_value = meta_value

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_page_meta_schema = FBPageMetaSchema()
    return fb_page_meta_schema.jsonify(fb_page_meta), 201


@ connex_app.route("/fb_page/meta/<fb_page_id>", methods=['GET'])
# @jwt_required
def get_fb_page_metas(fb_page_id):
    meta_key = request.args.get('meta_key', None)
    meta_value = request.args.get('meta_value', None)

    fb_page_metas = orm_get_fb_page_metas(fb_page_id, meta_key, meta_value)
    if not fb_page_metas:
        return jsonify({"msg": "FB Page meta not found."}), 404

    fb_page_meta_schema = FBPageMetaSchema(many=True)
    return fb_page_meta_schema.jsonify(fb_page_metas), 200


@ connex_app.route("/fb_page/meta/<fb_page_id>", methods=['DELETE'])
# @jwt_required
def delete_fb_page_meta(fb_page_id):
    meta_key = request.args.get('meta_key', None)
    meta_value = request.args.get('meta_value', None)

    fb_page_metas = orm_get_fb_page_metas(fb_page_id, meta_key, meta_value)
    if not fb_page_metas:
        return jsonify({"msg": "FB Page meta not found."}), 404

    try:
        for fb_page_meta in fb_page_metas:
            db.session.delete(fb_page_meta)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    return jsonify({"msg": f'Deletion: {len(fb_page_metas)}'}), 200


#
# FB Page Utilities
#


@ connex_app.route("/fb_page/list/<fb_user_id>", methods=['GET'])
# @jwt_required
def get_user_fb_page_list(fb_user_id):
    user = orm_get_user(fb_user_id)
    if not user:
        return jsonify({"msg": "User not found."}), 404

    try:
        result = fb_api_get_page_list_from_token(
            user.fb_user_token, user.fb_user_id)
    except:
        return jsonify({"msg": "FB API failed.",
                        "Traceback": traceback.format_exc()}), 500

    return jsonify(result), 200


# #
# # Deprecated
# #


# # FIXME NOT IMPORTANT
# @ connex_app.route("/fb_page/<user_id>/<fb_page_id>", methods=['GET'])
# # @jwt_required
# def get_user_fb_page_posts(user_id, fb_page_id):
#     try:
#         fb_user_token = User.query.filter_by(user_id=user_id).first()
#     except:
#         logger.error(traceback.format_exc())
#         return jsonify({"msg": "DB query GET failed."}), 500
#     # Emtpy query result
#     if not fb_user_token:
#         return jsonify({"msg": "User ID not found."}), 404

#     try:
#         fb_page_token = FBPage.query.get(
#             {"fb_user_id": fb_user_token.fb_user_id, "fb_page_id": fb_page_id})
#     except:
#         logger.error(traceback.format_exc())
#         return jsonify({"msg": "DB query GET failed."}), 500
#     # Emtpy query result
#     if not fb_page_token:
#         return jsonify({"msg": "FB Page ID not found."}), 404

#     try:
#         posts_on_page = fb_api_get_posts(
#             fb_page_token.fb_page_token, fb_page_id)
#     except:
#         return jsonify({"msg": "FB API failed.",
#                         "Traceback": traceback.format_exc()}), 500

#     return jsonify(posts_on_page), 200


# # FIXME NOT IMPORTANT
# @ connex_app.route("/fb_page/<fb_user_id>/<fb_page_id>/<fb_post_id>", methods=['GET'])
# # @jwt_required
# def get_user_fb_post_comments(fb_user_id, fb_page_id, fb_post_id):
#     try:
#         user = orm_get_user(fb_user_id)
#     except:
#         logger.error(traceback.format_exc())
#         return jsonify({"msg": "DB query GET failed."}), 500
#     # Emtpy query result
#     if not user:
#         return jsonify({"msg": "User ID not found."}), 404

#     try:
#         fb_page_token = orm_get_fb_page_token(fb_page_id)
#     except:
#         logger.error(traceback.format_exc())
#         return jsonify({"msg": "DB query GET failed."}), 500
#     # Emtpy query result
#     if not fb_page_token:
#         return jsonify({"msg": "FB Page ID not found."}), 404

#     try:
#         # Limits can be changed, currently set at 100
#         commens_in_post = fb_api_get_comments(
#             fb_page_token.fb_page_token, fb_post_id)
#     except:
#         return jsonify({"msg": "FB API failed.",
#                         "Traceback": traceback.format_exc()}), 500

#     return jsonify(commens_in_post), 200


# # FIXME NOT IMPORTANT
# @ connex_app.route('/fb_page/post_page_message', methods=['POST'])
# # @jwt_required
# def user_fb_post_page_message():
#     data = request.get_json()
#     # If there's no data provided
#     if not data:
#         return jsonify({"msg": "Data needed."}), 400

#     fb_page_token = data['page_token']

#     try:
#         ret = page_send_message(fb_page_token, data)
#     except:
#         return jsonify({"msg": "FB API failed.",
#                         "Traceback": traceback.format_exc()}), 500

#     return jsonify(ret), 200
