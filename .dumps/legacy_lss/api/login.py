from config import jwt, logger
from flask import request, jsonify
import traceback
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
from models.user_model import User, UserSchema

# Remove this after swagger implemented
from config import connex_app


"""TODO"""


@ connex_app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    try:
        user = User.query.filter_by(username=username).first()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500

    # Check for user the password
    if user is None or password != user.password:
        return jsonify({"msg": "Bad username or password"}), 401

    # This will also call the @ jwt.user_claims_loader to add claims data
    ret = {'access_token': create_access_token(user.user_id)}

    return jsonify(ret), 200


@ connex_app.route('/me', methods=['GET'])
@jwt_required
def me():
    # Access the identity of the current user with get_jwt_identity
    user_id = get_jwt_identity()

    try:
        user = User.query.get(user_id)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500

    user_basic_info_schema = UserSchema()
    return user_basic_info_schema.jsonify(user), 200


# This is for testing and see the claims of JWT
@ connex_app.route('/test_token', methods=['GET'])
@jwt_required
def test_token():
    # Access the identity of the current user with get_jwt_identity
    user_id = get_jwt_identity()
    ret = {'user_id': user_id}

    # Access the claims of the current user with get_jwt_claims
    # claims = get_jwt_claims()
    # ret = {'user_id': claims.get('user_id', None)}

    return jsonify(ret), 200


# For API tester log in
@ connex_app.route('/tester_login', methods=['POST'])
def tester_login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if username != 'algotech_api_test' or password != 'f8W==Kn_T2gv4kE6d+Qgw$b@6qfF-eRrB7hb*f!g^Ky8YH7ZPt':
        return jsonify({"msg": "Bad username or password"}), 401

    # This will also call the @ jwt.user_claims_loader to add claims data
    ret = {'access_token': create_access_token(username)}

    return jsonify(ret), 200


# This is for api endpoints access
@ connex_app.route('/create_api_token', methods=['POST'])
@jwt_required
def create_api_token():
    # Access the claims of the current user with get_jwt_claims
    claims = get_jwt_claims()

    token = create_access_token(claims.get('user_id', None),
                                expires_delta=False)

    return jsonify({'token': token,
                    'identity': claims.get('user_id', None),
                    'expires_delta': False}), 201


@ jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return {
        'user_id': identity
    }
