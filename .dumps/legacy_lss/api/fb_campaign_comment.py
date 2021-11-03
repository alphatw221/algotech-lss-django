from config import db, logger
from flask import jsonify, request
import traceback
# Import models from models directory
from models.fb_campaign_model import FBCampaignComment, FBCampaignCommentSchema
from api.utilities.api_orm_utilities import *
from api.utilities.api_utilities import *
from api.utilities.fb_api_utilities import *
from api.utilities.fb_campaign_utilities import *

from config import connex_app


@ connex_app.route("/fb_campaign/comment/<fb_campaign_id>", methods=['GET'])
# @jwt_required
def get_fb_campaign_comments(fb_campaign_id):
    # Handles the parameters that filter the order by start_time
    start_time = request.args.get('start_time', 0)
    filter_start_time = FBCampaignComment.created_time > start_time

    # Handles the parameters that filter the order by end_time
    end_time = request.args.get('end_time', None)
    if not end_time:
        filter_end_time = FBCampaignComment.created_time != None
    else:
        filter_end_time = FBCampaignComment.created_time < end_time

    try:
        fb_campaign_comments = FBCampaignComment.query.filter(
            FBCampaignComment.fb_campaign_id == fb_campaign_id,
            filter_start_time,
            filter_end_time
        ).order_by(FBCampaignComment.created_time.asc()).limit(100).all()
        if not fb_campaign_comments:
            return jsonify({"msg": "Campaign comment not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_comment_schema = FBCampaignCommentSchema(many=True)
    return fb_campaign_comment_schema.jsonify(fb_campaign_comments), 200
