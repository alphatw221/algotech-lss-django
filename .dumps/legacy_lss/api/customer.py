from config import db, logger
from flask import jsonify, request
import traceback
# Import models from models directory
from models.customer_model import (
    Customer, CustomerSchema,
    CustomerMeta, CustomerMetaSchema,
    CustomerAddress, CustomerAddressSchema
)
from api.utilities.fb_api_utilities import *

# Remove this after swagger implemented
from config import connex_app


#
# Customer
#


@ connex_app.route("/customer", methods=['POST'])
# @jwt_required
def create_customer():
    data = request.get_json()
    # If there's no data provided
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    fb_user_id = data.get('fb_user_id', None)
    if not fb_user_id:
        return jsonify({"msg": "Bad input data. Need: fb_user_id"}), 400

    try:
        # Create new customer
        new_customer = Customer(
            email=data.get('email', ""),
            fb_user_id=fb_user_id,
            fb_user_name=data.get('fb_user_name', ""),
            fb_token=data.get('fb_token', ""),
            remark=data.get('remark', ""),
        )
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object init failed."}), 500
    try:
        db.session.add(new_customer)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query ADD failed."}), 500

    customer_schema = CustomerSchema()
    return customer_schema.jsonify(new_customer), 201


@ connex_app.route("/customer/<fb_user_id>", methods=['GET'])
# @jwt_required
def get_customers(fb_user_id):
    try:
        customer = Customer.query.filter_by(fb_user_id=fb_user_id).first()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not customer:
        return jsonify({"msg": "Customer not found."}), 404

    customer_schema = CustomerSchema()
    return customer_schema.jsonify(customer), 200


@ connex_app.route("/customer/<customer_id>", methods=['PUT'])
# @jwt_required
def update_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not customer:
        return jsonify({"msg": "Customer not found."}), 404

    data = request.get_json()
    # If there's no update data provided
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'id', 'fb_user_id'}
    # Update each attr name in the given json
    for attr_name, updated_value in data.items():
        # Check for keys that not allowed to update
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            setattr(customer, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())
            return jsonify({"msg": "DB object setattr failed."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query UPDATE failed."}), 500

    customer_schema = CustomerSchema()
    return customer_schema.jsonify(customer), 200


@ connex_app.route("/customer/<customer_id>", methods=['DELETE'])
# @jwt_required
def delete_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not customer:
        return jsonify({"msg": "Customer not found."}), 404

    try:
        db.session.delete(customer)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object delete failed."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query DELETE failed."}), 500

    customer_schema = CustomerSchema()
    return customer_schema.jsonify(customer), 200


#
# Customer Meta
#


@ connex_app.route("/customer/meta", methods=['POST', 'PUT'])
# @jwt_required
def update_customer_meta():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    customer_id = data.get('customer_id', None)
    meta_key = data.get('meta_key', None)
    if not customer_id:
        return jsonify({"msg": "Bad input data. Need: customer_id"}), 400
    if not meta_key:
        return jsonify({"msg": "Bad input data. Need: meta_key"}), 400

    # Check if the customer meta is already existed
    try:
        customer_meta = CustomerMeta.query.filter_by(
            customer_id=customer_id, meta_key=meta_key).first()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500

    # If existed, update the value
    if customer_meta:
        customer_meta.meta_value = data.get('meta_value', '')

        try:
            db.session.commit()
        except:
            logger.error(traceback.format_exc())
            return jsonify({"msg": "DB query UPDATE failed."}), 500
    # If not existed, create a new one
    else:
        try:
            customer_meta = CustomerMeta(
                customer_id=customer_id,
                meta_key=meta_key,
                meta_value=data.get('meta_value', "")
            )
        except:
            logger.error(traceback.format_exc())
            return jsonify({"msg": "DB object init failed."}), 500
        try:
            db.session.add(customer_meta)
            db.session.commit()
        except:
            logger.error(traceback.format_exc())
            return jsonify({"msg": "DB query ADD failed."}), 500

    customer_meta_schema = CustomerMetaSchema()
    return customer_meta_schema.jsonify(customer_meta), 201


@ connex_app.route("/customer/meta", methods=['GET'])
# @jwt_required
def get_customer_meta():
    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = CustomerMeta.id == id
    else:
        filter_id = CustomerMeta.id != None

    # Handles the parameters customer_id
    customer_id = request.args.get('customer_id', None)
    if customer_id:
        filter_customer_id = CustomerMeta.customer_id == customer_id
    else:
        filter_customer_id = CustomerMeta.customer_id != None

    # Handles the parameters meta_key
    meta_key = request.args.get('meta_key', None)
    if meta_key:
        filter_meta_key = CustomerMeta.meta_key == meta_key
    else:
        filter_meta_key = CustomerMeta.meta_key != None

    # Handles the parameters meta_value
    meta_value = request.args.get('meta_value', None)
    if meta_value:
        filter_meta_value = CustomerMeta.meta_value == meta_value
    else:
        filter_meta_value = CustomerMeta.meta_value != None

    try:
        customer_metas = CustomerMeta.query.filter(
            filter_id,
            filter_customer_id,
            filter_meta_key,
            filter_meta_value
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not customer_metas:
        return jsonify({"msg": "Customer meta not found."}), 404

    customer_meta_schema = CustomerMetaSchema(many=True)
    return customer_meta_schema.jsonify(customer_metas), 200


@ connex_app.route("/customer/meta", methods=['DELETE'])
# @jwt_required
def delete_customer_meta():
    # Will delete the entire table if no parameters are given
    if len(request.args) == 0:
        return jsonify({"msg": "Parameters needed."}), 400

    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = CustomerMeta.id == id
    else:
        filter_id = CustomerMeta.id != None

    # Handles the parameters customer_id
    customer_id = request.args.get('customer_id', None)
    if customer_id:
        filter_customer_id = CustomerMeta.customer_id == customer_id
    else:
        filter_customer_id = CustomerMeta.customer_id != None

    # Handles the parameters meta_key
    meta_key = request.args.get('meta_key', None)
    if meta_key:
        filter_meta_key = CustomerMeta.meta_key == meta_key
    else:
        filter_meta_key = CustomerMeta.meta_key != None

    # Handles the parameters meta_value
    meta_value = request.args.get('meta_value', None)
    if meta_value:
        filter_meta_value = CustomerMeta.meta_value == meta_value
    else:
        filter_meta_value = CustomerMeta.meta_value != None

    try:
        customer_metas = CustomerMeta.query.filter(
            filter_id,
            filter_customer_id,
            filter_meta_key,
            filter_meta_value
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not customer_metas:
        return jsonify({"msg": "Customer meta not found."}), 404

    # Stat for return
    num_of_deletion = len(customer_metas)

    try:
        for customer_meta in customer_metas:
            db.session.delete(customer_meta)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object delete failed."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query DELETE failed."}), 500

    return jsonify({"Number of deletion": num_of_deletion}), 200


#
# Cusomter Address
#


@ connex_app.route("/customer/address/<customer_id>", methods=['POST'])
# @jwt_required
def create_customer_address(customer_id):
    data = request.get_json()
    # If there's no data provided
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    try:
        # Create new customer address
        new_customer_address = CustomerAddress(
            customer_id=customer_id,
            firstname=data.get('firstname', ''),
            lastname=data.get('lastname', ''),
            company=data.get('company', ''),
            address_1=data.get('address_1', ''),
            address_2=data.get('address_2', ''),
            city=data.get('city', ''),
            postcode=data.get('postcode', ''),
            country_id=data.get('country_id', ''),
            custom_field=data.get('custom_field', '')
        )
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object init failed."}), 500

    try:
        db.session.add(new_customer_address)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query ADD failed."}), 500

    customer_address_schema = CustomerAddressSchema()
    return customer_address_schema.jsonify(new_customer_address), 201


@ connex_app.route("/customer/address/<customer_id>", methods=['GET'])
# @jwt_required
def get_customer_addresses(customer_id):
    try:
        customer_addresses = CustomerAddress.query.filter_by(
            customer_id=customer_id).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not customer_addresses:
        return jsonify({"msg": "Customer address not found."}), 404

    customer_address_schema = CustomerAddressSchema(many=True)
    return customer_address_schema.jsonify(customer_addresses), 200


@ connex_app.route("/customer/address/<customer_id>/<address_id>", methods=['GET'])
# @jwt_required
def get_customer_address(customer_id, address_id):
    try:
        customer_address = CustomerAddress.query.get(address_id)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not customer_address:
        return jsonify({"msg": "Customer address not found."}), 404

    customer_address_schema = CustomerAddressSchema()
    return customer_address_schema.jsonify(customer_address), 200


@ connex_app.route("/customer/address/<customer_id>/<address_id>", methods=['PUT'])
# @jwt_required
def udpate_customer_address(customer_id, address_id):
    try:
        customer_address = CustomerAddress.query.get(address_id)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not customer_address:
        return jsonify({"msg": "Customer address not found."}), 404

    data = request.get_json()
    # If there's no update data provided
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    # Update each attr name in the given json
    for attr_name, updated_value in data.items():
        try:
            setattr(customer_address, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())
            return jsonify({"msg": "DB object setattr failed."}), 500

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query UPDATE failed."}), 500

    customer_address_schema = CustomerAddressSchema()
    return customer_address_schema.jsonify(customer_address), 200


@ connex_app.route("/customer/address/<customer_id>/<address_id>", methods=['DELETE'])
# @jwt_required
def delete_customer_address(customer_id, address_id):
    try:
        customer_address = CustomerAddress.query.get(address_id)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not customer_address:
        return jsonify({"msg": "Customer address not found."}), 404

    try:
        db.session.delete(customer_address)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object delete failed."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query DELETE failed."}), 500

    customer_address_schema = CustomerAddressSchema()
    return customer_address_schema.jsonify(customer_address), 200
