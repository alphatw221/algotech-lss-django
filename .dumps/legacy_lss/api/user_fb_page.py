
from config import db, logger
from flask import jsonify, request
import traceback
# Import models from models directory
from models.user_model import UserFBPage, UserFBPageSchema
from flask_jwt_extended import jwt_required
from api.utilities.api_orm_utilities import *
from datetime import datetime

# Remove this after swagger implemented
from config import connex_app


@ connex_app.route("/user/fb_page/<fb_user_id>/<fb_page_id>", methods=['POST'])
# @jwt_required
def create_user_fb_page(fb_user_id, fb_page_id):
    user_fb_page = orm_get_user_fb_page(
        fb_user_id=fb_user_id, fb_page_id=fb_page_id)
    if not user_fb_page:
        user_fb_page = UserFBPage(
            fb_user_id=fb_user_id,
            fb_page_id=fb_page_id
        )
        db.session.add(user_fb_page)
    else:
        user_fb_page.fb_user_id = fb_user_id
        user_fb_page.fb_page_id = fb_page_id
        user_fb_page.updated_at = datetime.now()

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    user_fb_page_schema = UserFBPageSchema()
    return user_fb_page_schema.jsonify(user_fb_page), 201


@ connex_app.route("/user/fb_page/<fb_user_id>", methods=['GET'])
# @jwt_required
def get_user_fb_pages(fb_user_id):
    try:
        user_fb_pages = UserFBPage.query.filter(
            UserFBPage.fb_user_id == fb_user_id
        ).all()
        if not user_fb_pages:
            return jsonify({"msg": "User FB Pages not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500

    user_fb_page_schema = UserFBPageSchema(many=True)
    return user_fb_page_schema.jsonify(user_fb_pages), 200


@ connex_app.route("/user/fb_page/<fb_user_id>/<fb_page_id>", methods=['PUT'])
# @jwt_required
def update_user_fb_page(fb_user_id, fb_page_id):
    try:
        user_fb_page = UserFBPage.query.filter(
            UserFBPage.fb_user_id == fb_user_id,
            UserFBPage.fb_page_id == fb_page_id
        ).first()
        if not user_fb_page:
            return jsonify({"msg": "User FB Pages not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500

    user_fb_page.fb_user_id = fb_user_id
    user_fb_page.fb_page_id = fb_page_id

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query UPDATE failed."}), 500

    user_fb_page_schema = UserFBPageSchema()
    return user_fb_page_schema.jsonify(user_fb_page), 200
