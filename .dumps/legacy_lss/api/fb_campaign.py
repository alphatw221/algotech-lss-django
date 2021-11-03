from config import db, logger
from flask import jsonify, request
from datetime import datetime
import traceback
# Import models from models directory
from models.fb_campaign_model import FBCampaign, FBCampaignSchema, CampaignMeta, CampaignMetaSchema
from api.utilities.fb_api_utilities import *
from api.utilities.api_orm_utilities import *

# Remove this after swagger implemented
from config import connex_app


#
# FB Campaign
#


@ connex_app.route("/fb_campaign/<fb_page_id>", methods=['POST'])
# @jwt_required
def create_fb_campaign(fb_page_id):
    fb_page = orm_get_fb_page(fb_page_id)
    if not fb_page:
        return jsonify({"msg": "FB Page not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    fb_user_id_added = data.get('fb_user_id_added', None)
    if not fb_user_id_added:
        return jsonify({"msg": "Bad input data. Need: fb_user_id_added"}), 400

    fb_post_id = data.get('fb_post_id', "")
    if not fb_post_id:
        fb_post_id = ''

    # Create new campaign
    try:
        fb_campaign = FBCampaign(
            fb_page_id=fb_page_id,
            fb_post_id=fb_post_id,
            fb_live_video_id=data.get('fb_live_video_id', ""),
            embed_url=data.get('embed_url', ""),
            title=data.get('title', ""),
            description=data.get('description', ""),
            status=data.get('status', ""),
            start_time=datetime.strptime(
                data.get('start_time', "2020-01-01T00:00:00")[0: 19], "%Y-%m-%dT%H:%M:%S"),
            end_time=datetime.strptime(
                data.get('end_time', "3000-01-01T00:00:00")[0: 19], "%Y-%m-%dT%H:%M:%S"),
            fb_user_id_added=fb_user_id_added
        )
        db.session.add(fb_campaign)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_schema = FBCampaignSchema()
    return fb_campaign_schema.jsonify(fb_campaign), 201


@ connex_app.route("/fb_campaign/<fb_page_id>", methods=['GET'])
# @jwt_required
def get_fb_campaigns(fb_page_id):
    fb_page = orm_get_fb_page(fb_page_id)
    if not fb_page:
        return jsonify({"msg": "FB Page not found."}), 404

    # Handles the parameters fb_campaign_id
    fb_campaign_id = request.args.get('fb_campaign_id', None)
    if fb_campaign_id:
        filter_fb_campaign_id = FBCampaign.fb_campaign_id == fb_campaign_id
    else:
        filter_fb_campaign_id = FBCampaign.fb_campaign_id != None

    # Handles the parameters that filter the fb_user_id_added
    fb_user_id_added = request.args.get('fb_user_id_added', None)
    if not fb_user_id_added:
        filter_fb_user_id_added = FBCampaign.fb_user_id_added != None
    else:
        filter_fb_user_id_added = FBCampaign.fb_user_id_added == fb_user_id_added

    # Handles the parameters that filter the fb_post_id
    fb_post_id = request.args.get('fb_post_id', None)
    if not fb_post_id:
        filter_fb_post_id = FBCampaign.fb_post_id != None
    else:
        filter_fb_post_id = FBCampaign.fb_post_id == fb_post_id

    # Handles the parameters that filter the fb_live_video_id
    fb_live_video_id = request.args.get('fb_live_video_id', None)
    if not fb_live_video_id:
        filter_fb_live_video_id = FBCampaign.fb_live_video_id != None
    else:
        filter_fb_live_video_id = FBCampaign.fb_live_video_id == fb_live_video_id

    # Handles the parameters that filter the title
    title = request.args.get('title', None)
    if not title:
        filter_title = FBCampaign.title != None
    else:
        filter_title = FBCampaign.title == title

    # Handles the parameters that filter the status
    status = request.args.get('status', None)
    if not status:
        filter_status = FBCampaign.status != None
    else:
        filter_status = FBCampaign.status == status

    try:
        fb_campaigns = FBCampaign.query.filter(
            FBCampaign.fb_page_id == fb_page_id,
            filter_fb_campaign_id,
            filter_fb_user_id_added,
            filter_fb_post_id,
            filter_fb_live_video_id,
            filter_title,
            filter_status
        ).all()
        if not fb_campaigns:
            return jsonify({"msg": "FB Campaign not found."}), 404
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500

    fb_campaign_schema = FBCampaignSchema(many=True)
    return fb_campaign_schema.jsonify(fb_campaigns), 200


@ connex_app.route("/fb_campaign/<fb_page_id>/<fb_campaign_id>", methods=['PUT'])
# @jwt_required
def update_fb_campaign(fb_page_id, fb_campaign_id):
    fb_page = orm_get_fb_page(fb_page_id)
    if not fb_page:
        return jsonify({"msg": "FB Page not found."}), 404

    fb_campaign = orm_get_fb_campaign(fb_campaign_id)
    if not fb_campaign:
        return jsonify({"msg": "FB Campaign not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Update data needed."}), 400

    UPDATE_NOT_ALLOWED = {'fb_campaign_id',
                          'fb_page_id', 'date_added', 'date_modified'}
    for attr_name, updated_value in data.items():
        if attr_name in UPDATE_NOT_ALLOWED:
            continue

        try:
            if attr_name == "start_time":
                fb_campaign.start_time = datetime.strptime(
                    data['start_time'][0: 19], "%Y-%m-%dT%H:%M:%S")
            elif attr_name == "end_time":
                fb_campaign.end_time = datetime.strptime(
                    data['end_time'][0: 19], "%Y-%m-%dT%H:%M:%S")
            elif updated_value == None:
                continue
            else:
                setattr(fb_campaign, attr_name, updated_value)
        except:
            logger.error(traceback.format_exc())
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_schema = FBCampaignSchema()
    return fb_campaign_schema.jsonify(fb_campaign), 200


@ connex_app.route("/fb_campaign/<fb_page_id>/<fb_campaign_id>", methods=['DELETE'])
# @jwt_required
def delete_fb_campaign(fb_page_id, fb_campaign_id):
    fb_page = orm_get_fb_page(fb_page_id)
    if not fb_page:
        return jsonify({"msg": "FB Page not found."}), 404

    fb_campaign = orm_get_fb_campaign(fb_campaign_id)
    if not fb_campaign:
        return jsonify({"msg": "FB Campaign not found."}), 404

    try:
        db.session.delete(fb_campaign)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    fb_campaign_schema = FBCampaignSchema()
    return fb_campaign_schema.jsonify(fb_campaign), 200


#
# Campaign Meta
#


@ connex_app.route("/campaign/meta/<fb_campaign_id>", methods=['POST', 'PUT'])
# @jwt_required
def update_campaign_meta(fb_campaign_id):
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    meta_key = data.get('meta_key', None)
    if not meta_key:
        return jsonify({"msg": "Bad input data. Need: meta_key"}), 400
    meta_value = data.get('meta_value', None)
    if not meta_value:
        meta_value = ''

    campaign_metas = orm_get_campaign_metas(
        fb_campaign_id=fb_campaign_id, meta_key=meta_key)
    if not campaign_metas:
        campaign_meta = CampaignMeta(
            fb_campaign_id=fb_campaign_id,
            meta_key=meta_key,
            meta_value=meta_value
        )
        db.session.add(campaign_meta)
    else:
        campaign_meta = next(iter(campaign_metas))
        campaign_meta.meta_value = meta_value

    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    campaign_meta_schema = CampaignMetaSchema()
    return campaign_meta_schema.jsonify(campaign_meta), 201


@ connex_app.route("/campaign/meta/<fb_campaign_id>", methods=['GET'])
# @jwt_required
def get_campaign_metas(fb_campaign_id):
    meta_key = request.args.get('meta_key', None)
    meta_value = request.args.get('meta_value', None)

    campaign_metas = orm_get_campaign_metas(
        fb_campaign_id, meta_key, meta_value)
    if not campaign_metas:
        return jsonify({"msg": "Campaign meta not found."}), 404

    campaign_meta_schema = CampaignMetaSchema(many=True)
    return campaign_meta_schema.jsonify(campaign_metas), 200


@ connex_app.route("/campaign/meta/<fb_campaign_id>", methods=['DELETE'])
# @jwt_required
def delete_campaign_meta(fb_campaign_id):
    meta_key = request.args.get('meta_key', None)
    meta_value = request.args.get('meta_value', None)

    campaign_metas = orm_get_campaign_metas(
        fb_campaign_id, meta_key, meta_value)
    if not campaign_metas:
        return jsonify({"msg": "Campaign meta not found."}), 404

    try:
        for campaign_meta in campaign_metas:
            db.session.delete(campaign_meta)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB error."}), 500

    return jsonify({"msg": f'Deletion: {len(campaign_metas)}'}), 200
