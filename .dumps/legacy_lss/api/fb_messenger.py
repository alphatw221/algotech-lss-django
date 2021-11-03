from config import db, logger
from flask import jsonify, request
# Import models from models directory
from models.fb_messenger_model import (
    FBMessengerAutoResponse, FBMessengerAutoResponseSchema
)
from api.utilities.fb_api_utilities import *

# Remove this after swagger implemented
from config import connex_app


@ connex_app.route("/fb_messenger/auto_response/<fb_page_id>", methods=['POST'])
# @jwt_required
def create_fb_messenger_auto_response(fb_page_id):
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    message_req = data.get('message_req', None)
    if not message_req:
        return jsonify({"msg": "Bad input data. Need: message_req"}), 400

    try:
        new_auto_response = FBMessengerAutoResponse(
            fb_page_id=fb_page_id,
            message_req=message_req,
            message_res=data.get('message_res', ""),
            message_type=data.get('message_type', ""),
            message_des=data.get('message_des', "")
        )
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object init failed."}), 500
    try:
        db.session.add(new_auto_response)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query ADD failed."}), 500

    auto_response_schema = FBMessengerAutoResponseSchema()
    return auto_response_schema.jsonify(new_auto_response), 201


@ connex_app.route("/fb_messenger/auto_response/<fb_page_id>", methods=['GET'])
# @jwt_required
def get_fb_messenger_auto_response(fb_page_id):
    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = FBMessengerAutoResponse.id == id
    else:
        filter_id = FBMessengerAutoResponse.id != None

    # Handles the parameters message_req
    message_req = request.args.get('message_req', None)
    if message_req:
        filter_message_req = FBMessengerAutoResponse.message_req == message_req
    else:
        filter_message_req = FBMessengerAutoResponse.message_req != None

    try:
        auto_responses = FBMessengerAutoResponse.query.filter(
            filter_id,
            FBMessengerAutoResponse.fb_page_id == fb_page_id,
            filter_message_req
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not auto_responses:
        return jsonify({"msg": "FB Messenger Auto Response not found."}), 404

    auto_response_schema = FBMessengerAutoResponseSchema(many=True)
    return auto_response_schema.jsonify(auto_responses), 200


@ connex_app.route("/fb_messenger/auto_response/<fb_page_id>", methods=['PUT'])
# @jwt_required
def udpate_fb_messenger_auto_response(fb_page_id):
    # Handles the parameters id
    id = request.args.get('id', None)
    if not id:
        return jsonify({"msg": "Bad input data. Need: id"}), 400

    try:
        auto_response = FBMessengerAutoResponse.query.get(id)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not auto_response:
        return jsonify({"msg": "FB Messenger Auto Response not found."}), 404

    data = request.get_json()
    # If there's no update data provided
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'id', 'fb_page_id'}
    # Update each attr name in the given json
    for attr_name, updated_value in data.items():
        # Check for keys that not allowed to update
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            setattr(auto_response, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())
            return jsonify({"msg": "DB object setattr failed."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query UPDATE failed."}), 500

    auto_response_schema = FBMessengerAutoResponseSchema()
    return auto_response_schema.jsonify(auto_response), 200


@ connex_app.route("/fb_messenger/auto_response/<fb_page_id>", methods=['DELETE'])
# @jwt_required
def delete_fb_messenger_auto_response(fb_page_id):
    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = FBMessengerAutoResponse.id == id
    else:
        filter_id = FBMessengerAutoResponse.id != None

    # Handles the parameters message_req
    message_req = request.args.get('message_req', None)
    if message_req:
        filter_message_req = FBMessengerAutoResponse.message_req == message_req
    else:
        filter_message_req = FBMessengerAutoResponse.message_req != None

    try:
        auto_responses = FBMessengerAutoResponse.query.filter(
            filter_id,
            FBMessengerAutoResponse.fb_page_id == fb_page_id,
            filter_message_req
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not auto_responses:
        return jsonify({"msg": "FB Messenger Auto Response not found."}), 404

    # Stat for return
    num_of_deletion = len(auto_responses)

    try:
        for auto_response in auto_responses:
            db.session.delete(auto_response)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object delete failed."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query DELETE failed."}), 500

    return jsonify({"Number of deletion": num_of_deletion}), 200
