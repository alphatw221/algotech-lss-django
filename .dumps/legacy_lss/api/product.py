from config import db, logger
from flask import jsonify, request
from datetime import datetime
import traceback
# Import models from models directory
from models.product_model import (
    Product, ProductSchema, ProductPreviewSchema,
    ProductDescription, ProductDescriptionSchema,
    ProductManufacturer, ProductManufacturerSchema,
    ProductMeta, ProductMetaSchema
)
from api.utilities.fb_api_utilities import *
from api.utilities.api_orm_utilities import *

# Remove this after swagger implemented
from config import connex_app


@ connex_app.route("/product", methods=['POST'])
# @jwt_required
def create_product():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    fb_user_id = data.get('fb_user_id', None)
    if not fb_user_id:
        return jsonify({"msg": "Bad input data. Need: fb_user_id"}), 400

    user = orm_get_user(fb_user_id)
    if not user:
        return jsonify({"msg": "User not found."}), 404

    try:
        # Create new product
        new_product = Product(
            fb_user_id=fb_user_id,
            max_order_amount=data.get('max_order_amount', 0),
            active_stat=data.get('active_stat', 0),
            product_type=data.get('product_type', ""),
            remark=data.get('remark', ""),

            modelname=data.get('modelname', ""),
            sku=data.get('sku', ""),
            upc=data.get('upc', ""),
            location=data.get('location', ""),
            quantity=data.get('quantity', 0),
            stock_status_id=data.get('stock_status_id', 0),
            image=data.get('image', ""),
            manufacturer_id=data.get('manufacturer_id', 0),
            shipping=data.get('shipping', 0),
            price=data.get('price', 0),
            price_two=data.get('price_two', 0),
            price_three=data.get('price_three', 0),
            points=data.get('points', 0),
            date_available=datetime.strptime(
                data.get('date_available', "2020-01-01T00:00:00"), "%Y-%m-%dT%H:%M:%S"),
            height=data.get('height', 0),
            subtract=data.get('subtract', 0),
            minimum=data.get('minimum', 0),
            sort_order=data.get('sort_order', 0),
            status=data.get('status', 0),
            viewed=data.get('viewed', 0)
        )
        db.session.add(new_product)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    product_schema = ProductSchema()
    return product_schema.jsonify(new_product), 201


@ connex_app.route("/product", methods=['GET'])
# @jwt_required
def get_products():
    # Handles the parameter: product_id
    product_id = request.args.get('product_id', None)
    if product_id:
        filter_product_id = Product.product_id == product_id
    else:
        filter_product_id = Product.product_id != None

    # Handles the parameter: fb_user_id
    fb_user_id = request.args.get('fb_user_id', None)
    if fb_user_id:
        filter_fb_user_id = Product.fb_user_id == fb_user_id
    else:
        filter_fb_user_id = Product.fb_user_id != None

    # Handles the parameter: active_stat
    active_stat = request.args.get('active_stat', None)
    if active_stat:
        filter_active_stat = Product.active_stat == active_stat
    else:
        filter_active_stat = Product.active_stat != None

    # Handles the parameter: product_type
    product_type = request.args.get('product_type', None)
    if product_type:
        filter_product_type = Product.product_type == product_type
    else:
        filter_product_type = Product.product_type != None

    try:
        products = Product.query.filter(
            filter_product_id,
            filter_fb_user_id,
            filter_active_stat,
            filter_product_type
        ).all()
        if not products:
            return jsonify({"msg": "Product not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    # Return preview i.e. only important information if preview in "On"
    if str(request.args.get('preview')) == "on":
        product_schema = ProductPreviewSchema(many=True)
    else:
        product_schema = ProductSchema(many=True)

    return product_schema.jsonify(products), 200


@ connex_app.route("/product/<product_id>", methods=['PUT'])
# @jwt_required
def update_product(product_id):
    product = orm_get_product(product_id)
    if not product:
        return jsonify({"msg": "Product not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'product_id', 'fb_user_id',
                          'date_added', 'date_modified'}
    for attr_name, updated_value in data.items():
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            if attr_name == "date_available":
                product.date_available = datetime.strptime(
                    data['date_available'], "%Y-%m-%dT%H:%M:%S")
            else:
                setattr(product, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    product_schema = ProductSchema()
    return product_schema.jsonify(product), 200


# @ connex_app.route("/product/<product_id>", methods=['DELETE']) #TODO DELETE THIS
# @jwt_required
def delete_product(product_id):
    product = orm_get_product(product_id)
    if not product:
        return jsonify({"msg": "Product not found."}), 404

    try:
        db.session.delete(product)

        # Delete all product description
        ProductDescription.query.filter_by(
            product_id=product_id).delete()

        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    product_schema = ProductSchema()
    return product_schema.jsonify(product), 200


#
# Product Description
#


@ connex_app.route("/product/description/<product_id>", methods=['POST'])
# @jwt_required
def create_product_description(product_id):
    product = orm_get_product(product_id)
    if not product:
        return jsonify({"msg": "Product not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    language_id = data.get('language_id', 0)
    product_description = orm_get_product_description(product_id, language_id)

    # If existed, update the value
    if product_description:
        product_description.name = data.get('name', "")
        product_description.description = data.get('description', "")
        product_description.tag = data.get('tag', "")
        product_description.order_code = data.get('order_code', "")
        product_description.meta_title = data.get('meta_title', "")
        product_description.meta_description = data.get(
            'meta_description', "")
        product_description.meta_keyword = data.get('meta_keyword', "")
    # If not existed, create a new one
    else:
        product_description = ProductDescription(
            product_id=product_id,
            language_id=language_id,
            name=data.get('name', ""),
            description=data.get('description', ""),
            tag=data.get('tag', ""),
            order_code=data.get('order_code', ""),
            meta_title=data.get('meta_title', ""),
            meta_description=data.get('meta_description', ""),
            meta_keyword=data.get('meta_keyword', "")
        )
        db.session.add(product_description)
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query ADD failed."}), 500

    product_description_schema = ProductDescriptionSchema()
    return product_description_schema.jsonify(product_description), 201


@ connex_app.route("/product/description/<product_id>", methods=['GET'])
# @jwt_required
def get_product_description(product_id):
    product = orm_get_product(product_id)
    if not product:
        return jsonify({"msg": "Product not found."}), 404

    language_id = request.args.get('language_id', 0)
    product_description = orm_get_product_description(product_id, language_id)
    if not product_description:
        return jsonify({"msg": "Product description not found."}), 404

    product_description_schema = ProductDescriptionSchema()
    return product_description_schema.jsonify(product_description), 200


@ connex_app.route("/product/description/list", methods=['GET'])
# @jwt_required
def get_product_descriptions_by_list():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    product_id_list = data.get('product_id_list', None)
    if not product_id_list:
        return jsonify({"msg": "Bad input data. Need: product_id_list"}), 400

    language_id = request.args.get('language_id', 0)

    product_description_list = []
    for product_id in product_id_list:
        product_description = orm_get_product_description(
            product_id, language_id)
        if product_description:
            product_description_list.append(product_description)
    if not product_description_list:
        return jsonify({"msg": "Product description not found."}), 404

    product_description_schema = ProductDescriptionSchema(many=True)
    return product_description_schema.jsonify(product_description_list), 200


@ connex_app.route("/product/description/user/<fb_user_id>", methods=['GET'])
# @jwt_required
def get_product_descriptions_by_fb_user_id(fb_user_id):
    language_id = request.args.get('language_id', 0)

    try:
        products = Product.query.filter(
            Product.fb_user_id == fb_user_id
        ).all()
        if not products:
            return jsonify({"msg": "Product not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500

    product_descriptions = []
    for product in products:
        try:
            product_description = ProductDescription.query.filter(
                ProductDescription.product_id == product.product_id,
                ProductDescription.language_id == language_id
            ).first()
            product_descriptions.append(product_description)

        except:
            logger.error(traceback.format_exc())
    if not product_descriptions:
        return jsonify({"msg": "Product description not found."}), 404

    product_description_schema = ProductDescriptionSchema(many=True)
    return product_description_schema.jsonify(product_descriptions), 200


@ connex_app.route("/product/description/<product_id>/<language_id>", methods=['PUT'])
# @jwt_required
def update_product_description(product_id, language_id):
    product = orm_get_product(product_id)
    if not product:
        return jsonify({"msg": "Product not found."}), 404

    product_description = orm_get_product_description(product_id, language_id)
    if not product_description:
        return jsonify({"msg": "Product description not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'product_id', 'language_id'}
    for attr_name, updated_value in data.items():
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            setattr(product_description, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    product_description_schema = ProductDescriptionSchema()
    return product_description_schema.jsonify(product_description), 200


@ connex_app.route("/product/description/<product_id>", methods=['DELETE'])
# @jwt_required
def delete_product_description(product_id):
    product = orm_get_product(product_id)
    if not product:
        return jsonify({"msg": "Product not found."}), 404

    language_id = request.args.get('language_id', None)

    if language_id:
        product_description = orm_get_product_description(
            product_id, language_id)
        if not product_description:
            return jsonify({"msg": "Product description not found."}), 404
        db.session.delete(product_description)
    else:
        try:
            ProductDescription.query.filter_by(
                product_id=product_id).delete()
        except:
            logger.error(traceback.format_exc())
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    return jsonify({"msg": 'Deletion: success'}), 200


#
# Product Manufacturer
#


@ connex_app.route("/product/manufacturer", methods=['POST'])
# @jwt_required
def create_product_manufacturer():
    data = request.get_json()
    # If there's no data provided
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    name = data.get('name', None)
    if not name:
        return jsonify({"msg": "Bad input data. Need: name"}), 400

    try:
        # Create new product
        new_product_manufacturer = ProductManufacturer(
            name=name,
            image=data.get('image', ""),
            sort_order=data.get('sort_order', 0)
        )
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object init failed."}), 500

    try:
        db.session.add(new_product_manufacturer)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query ADD failed."}), 500

    product_manufacturer_schema = ProductManufacturerSchema()
    return product_manufacturer_schema.jsonify(new_product_manufacturer), 201


@ connex_app.route("/product/manufacturer/<manufacturer_id>", methods=['GET'])
# @jwt_required
def get_product_manufacturer(manufacturer_id):
    try:
        product_manufacturer = ProductManufacturer.query.get(manufacturer_id)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not product_manufacturer:
        return jsonify({"msg": "Product manufacturer not found."}), 404

    product_manufacturer_schema = ProductManufacturerSchema()
    return product_manufacturer_schema.jsonify(product_manufacturer), 200


@ connex_app.route("/product/manufacturer/<manufacturer_id>", methods=['PUT'])
# @jwt_required
def update_product_manufacturer(manufacturer_id):
    try:
        product_manufacturer = ProductManufacturer.query.get(manufacturer_id)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not product_manufacturer:
        return jsonify({"msg": "Product manufacturer not found."}), 404

    data = request.get_json()
    # If there's no update data provided
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'id'}
    # Update each attr name in the given json
    for attr_name, updated_value in data.items():
        # Check for keys that not allowed to update
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            setattr(product_manufacturer, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())
            return jsonify({"msg": "DB object setattr failed."}), 500

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query UPDATE failed."}), 500

    product_manufacturer_schema = ProductManufacturerSchema()
    return product_manufacturer_schema.jsonify(product_manufacturer), 200


@ connex_app.route("/product/manufacturer/<manufacturer_id>", methods=['DELETE'])
# @jwt_required
def delete_product_manufacturer(manufacturer_id):
    try:
        product_manufacturer = ProductManufacturer.query.get(manufacturer_id)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not product_manufacturer:
        return jsonify({"msg": "Product manufacturer not found."}), 404

    try:
        db.session.delete(product_manufacturer)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object delete failed."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query DELETE failed."}), 500

    product_manufacturer_schema = ProductManufacturerSchema()
    return product_manufacturer_schema.jsonify(product_manufacturer), 200


#
# Product Meta
#


@ connex_app.route("/product/meta", methods=['POST', 'PUT'])
# @jwt_required
def update_product_meta():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    product_id = data.get('product_id', None)
    meta_key = data.get('meta_key', None)
    if not product_id:
        return jsonify({"msg": "Bad input data. Need: product_id"}), 400
    if not meta_key:
        return jsonify({"msg": "Bad input data. Need: meta_key"}), 400

    # Check if the product meta is already existed
    try:
        product_meta = ProductMeta.query.filter_by(
            product_id=product_id, meta_key=meta_key).first()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    # If existed, update the value
    if product_meta:
        product_meta.meta_value = data.get('meta_value', '')
    else:
        product_meta = ProductMeta(
            product_id=product_id,
            meta_key=meta_key,
            meta_value=data.get('meta_value', "")
        )
        db.session.add(product_meta)

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    product_meta_schema = ProductMetaSchema()
    return product_meta_schema.jsonify(product_meta), 201


@ connex_app.route("/product/meta", methods=['GET'])
# @jwt_required
def get_product_meta():
    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = ProductMeta.id == id
    else:
        filter_id = ProductMeta.id != None

    # Handles the parameters product_id
    product_id = request.args.get('product_id', None)
    if product_id:
        filter_product_id = ProductMeta.product_id == product_id
    else:
        filter_product_id = ProductMeta.product_id != None

    # Handles the parameters meta_key
    meta_key = request.args.get('meta_key', None)
    if meta_key:
        filter_meta_key = ProductMeta.meta_key == meta_key
    else:
        filter_meta_key = ProductMeta.meta_key != None

    # Handles the parameters meta_value
    meta_value = request.args.get('meta_value', None)
    if meta_value:
        filter_meta_value = ProductMeta.meta_value == meta_value
    else:
        filter_meta_value = ProductMeta.meta_value != None

    try:
        product_metas = ProductMeta.query.filter(
            filter_id,
            filter_product_id,
            filter_meta_key,
            filter_meta_value
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    # Emtpy query result
    if not product_metas:
        return jsonify({"msg": "Product meta not found."}), 404

    product_meta_schema = ProductMetaSchema(many=True)
    return product_meta_schema.jsonify(product_metas), 200


@ connex_app.route("/product/meta", methods=['DELETE'])
# @jwt_required
def delete_product_meta():
    # Will delete the entire table if no parameters are given
    if len(request.args) == 0:
        return jsonify({"msg": "Parameters needed."}), 400

    # Handles the parameters id
    id = request.args.get('id', None)
    if id:
        filter_id = ProductMeta.id == id
    else:
        filter_id = ProductMeta.id != None

    # Handles the parameters product_id
    product_id = request.args.get('product_id', None)
    if product_id:
        filter_product_id = ProductMeta.product_id == product_id
    else:
        filter_product_id = ProductMeta.product_id != None

    # Handles the parameters meta_key
    meta_key = request.args.get('meta_key', None)
    if meta_key:
        filter_meta_key = ProductMeta.meta_key == meta_key
    else:
        filter_meta_key = ProductMeta.meta_key != None

    # Handles the parameters meta_value
    meta_value = request.args.get('meta_value', None)
    if meta_value:
        filter_meta_value = ProductMeta.meta_value == meta_value
    else:
        filter_meta_value = ProductMeta.meta_value != None

    try:
        product_metas = ProductMeta.query.filter(
            filter_id,
            filter_product_id,
            filter_meta_key,
            filter_meta_value
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500
    # Emtpy query result
    if not product_metas:
        return jsonify({"msg": "Product meta not found."}), 404

    # Stat for return
    num_of_deletion = len(product_metas)

    try:
        for product_meta in product_metas:
            db.session.delete(product_meta)
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
# Product Bulk Create
#

@ connex_app.route("/product/<fb_user_id>/bulk", methods=['POST'])
# @jwt_required
def create_product_bulk(fb_user_id):
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400
    if not isinstance(data, list):
        return jsonify({'data': 'This field is required to be an array.'}), 400

    product_created = 0
    for row in data:
        product = orm_create_product_default(
            fb_user_id=fb_user_id,
            name=row.get("name", ""),
            description=row.get("description", ""),
            order_code=row.get("order_code", ""),
            price=row.get("price", 0),
            max_order_amount=row.get("max_order_amount", 0),
            quantity=row.get("quantity", 0),
            product_type=row.get("product_type", "product")
        )
        if product:
            product_created += 1

    return jsonify({"product_created": product_created}), 201
