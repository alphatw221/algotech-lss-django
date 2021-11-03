from config import db, logger
from flask import json, jsonify, request
import traceback
from api.utilities.fb_api_utilities import *
from api.utilities.api_orm_utilities import *


# Remove this after swagger implemented
from config import connex_app


# #
# # User Group
# #


# @ connex_app.route("/user_group", methods=['POST'])
# # @jwt_required
# def create_user_group():
#     data = request.get_json()
#     if not data:
#         return jsonify({"msg": "Data needed."}), 400

#     user_group = UserGroup(
#         name=data.get('name', ''),
#         description=data.get('description', ''),
#         max_campaign=data.get('max_campaign', 0),
#         max_campaign_time=data.get('max_campaign_time', 0),
#         max_product_sold=data.get('max_product_sold', 0),
#         max_transaction=data.get('max_transaction', 0),
#         max_transaction_amount=data.get('max_transaction_amount', 0)
#     )
#     try:
#         db.session.add(user_group)
#         db.session.commit()
#     except:
#         logger.error(traceback.format_exc())
#         return jsonify({"msg": "DB error."}), 500

#     user_group_schema = UserGroupSchema()
#     return user_group_schema.jsonify(user_group), 200


# @ connex_app.route("/user_group/<id>", methods=['GET'])
# # @jwt_required
# def get_user_group(id):
#     user_group = orm_get_user_group(id)
#     if not user_group:
#         return jsonify({"msg": "User group not found."}), 404

#     user_group_schema = UserGroupSchema()
#     return user_group_schema.jsonify(user_group), 200


# @ connex_app.route("/user_group", methods=['GET'])
# # @jwt_required
# def get_user_groups():
#     user_groups = orm_get_user_groups()
#     if not user_groups:
#         return jsonify({"msg": "User group not found."}), 404

#     user_group_schema = UserGroupSchema(many=True)
#     return user_group_schema.jsonify(user_groups), 200


# @ connex_app.route("/user_group/<id>", methods=['PUT'])
# # @jwt_required
# def update_user_group(id):
#     user_group = orm_get_user_group(id)
#     if not user_group:
#         return jsonify({"msg": "User group not found."}), 404

#     data = request.get_json()
#     if not data:
#         return jsonify({"msg": "Update data needed."}), 400

#     UPDATE_NOT_ALLOWED = {'id', }
#     for attr_name, updated_value in data.items():
#         if attr_name in UPDATE_NOT_ALLOWED:
#             continue
#         try:
#             setattr(user_group, attr_name, updated_value)
#         except:
#             logger.error(traceback.format_exc())

#     try:
#         db.session.commit()
#     except:
#         logger.error(traceback.format_exc())
#         return jsonify({"msg": "DB error."}), 500

#     user_group_schema = UserGroupSchema()
#     return user_group_schema.jsonify(user_group), 200


# @ connex_app.route("/user_group/<id>", methods=['DELETE'])
# # @jwt_required
# def delete_user_group(id):
#     user_group = orm_get_user_group(id)
#     if not user_group:
#         return jsonify({"msg": "User group not found."}), 404

#     try:
#         db.session.delete(user_group)
#         db.session.commit()
#     except:
#         logger.error(traceback.format_exc())
#         return jsonify({"msg": "DB error."}), 500

#     user_group_schema = UserGroupSchema()
#     return user_group_schema.jsonify(user_group), 200


# #
# # User Group Users
# #

# @ connex_app.route("/user_group_users", methods=['POST'])
# # @jwt_required
# def create_user_group_users():
#     data = request.get_json()
#     if not data:
#         return jsonify({"msg": "Data needed."}), 400

#     user_group_id = data.get('user_group_id')
#     user_id = data.get('user_id')
#     if not user_group_id:
#         return jsonify({"msg": "Bad input data. Need: user_group_id"}), 400
#     if not user_id:
#         return jsonify({"msg": "Bad input data. Need: user_id"}), 400

#     user_group_user = UserGroupUsers(
#         user_group_id=user_group_id,
#         user_id=user_id
#     )
#     try:
#         db.session.merge(user_group_user)
#         db.session.commit()
#     except Exception as e:
#         logger.error(traceback.format_exc())
#         return jsonify({"msg": f"{e}"}), 500

#     user_group_users_schema = UserGroupUsersSchema()
#     return user_group_users_schema.jsonify(user_group_user), 200


# @ connex_app.route("/user_group_users/<user_group_id>", methods=['GET'])
# # @jwt_required
# def get_user_group_users(user_group_id):
#     try:
#         user_group_users = UserGroupUsers.query.filter(
#             UserGroupUsers.user_group_id == user_group_id
#         ).all()
#         if not user_group_users:
#             return jsonify({"msg": "User group users not found."}), 404
#     except:
#         logger.error(traceback.format_exc())
#         return jsonify({"msg": "User group users not found."}), 404

#     user_group_users_schema = UserGroupUsersSchema(many=True)
#     return user_group_users_schema.jsonify(user_group_users), 200


# @ connex_app.route("/user_group_users/<id>", methods=['DELETE'])
# # @jwt_required
# def delete_user_group_users(id):
#     try:
#         user_group_user = UserGroupUsers.query.get(id)
#         if not user_group_user:
#             return jsonify({"msg": "User group users not found."}), 404
#     except:
#         logger.error(traceback.format_exc())
#         return jsonify({"msg": "User group users not found."}), 404

#     try:
#         db.session.delete(user_group_user)
#         db.session.commit()
#     except:
#         logger.error(traceback.format_exc())
#         return jsonify({"msg": "DB error."}), 500

#     user_group_users_schema = UserGroupUsersSchema()
#     return user_group_users_schema.jsonify(user_group_user), 200
