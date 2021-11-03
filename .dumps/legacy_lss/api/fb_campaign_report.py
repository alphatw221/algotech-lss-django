from config import db, logger
from flask import jsonify, request
import traceback
# Import models from models directory
from models.fb_campaign_model import FBCampaign, FBCampaignSchema, CampaignMeta, CampaignMetaSchema
from api.utilities.fb_campaign_summary import create_fb_campaign_summary
from api.utilities.api_orm_utilities import *

# Remove this after swagger implemented
from config import connex_app


@ connex_app.route("/fb_campaign_report/<fb_campaign_id>", methods=['POST'])
# @jwt_required
def create_fb_campaign_report(fb_campaign_id):
    fb_campaign = orm_get_fb_campaign(fb_campaign_id)
    if not fb_campaign:
        return jsonify({"msg": "FB Campaign not found."}), 404

    file_name = None
    order_status = None

    data = request.get_json()
    if data:
        file_name = data.get('file_name', None)
        order_status = data.get('order_status', None)

    try:
        create_fb_campaign_summary(
            fb_campaign_id,
            file_name=file_name,
            order_status=order_status
        )
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "Internal error."}), 500

    fb_campaign_schema = FBCampaignSchema()
    return fb_campaign_schema.jsonify(fb_campaign), 201
