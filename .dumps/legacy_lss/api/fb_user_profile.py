from config import db, logger
from flask import jsonify, request
import traceback
# Import models from models directory
from api.utilities.api_orm_utilities import *
from api.utilities.api_utilities import *
from api.utilities.fb_api_utilities import *
from api.utilities.fb_campaign_utilities import *

from config import connex_app


@ connex_app.route("/fb_user_profile/<fb_user_id>", methods=['GET'])
# @jwt_required
def get_fb_user_profile_by_fb_user_id(fb_user_id):
    fb_campaign_comment = orm_get_fb_campaign_comment_by_fb_user_id(fb_user_id)
    if not fb_campaign_comment:
        return jsonify({"msg": "FB User Profile not found."}), 404

    return jsonify({"fb_user_name": fb_campaign_comment.fb_user_name,
                    "picture_url": fb_campaign_comment.picture_url}), 200
