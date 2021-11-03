from config import db, logger
from flask import jsonify, request
import random
import json
import traceback
# Import models from models directory
from models.fb_campaign_model import (
    FBLuckyDraw, FBLuckyDrawSchema,
    FBCampaignComment, FBCampaignOrder
)
from api.utilities.fb_api_utilities import *
from api.utilities.api_utilities import *
from api.utilities.fb_campaign_utilities import *

# Remove this after swagger implemented
from config import connex_app


@ connex_app.route("/fb_campaign/lucky_draw/<fb_campaign_id>", methods=['POST'])
# @jwt_required
def create_fb_campaign_lucky_draw(fb_campaign_id):
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    # Check the important input data
    prize_product_id = data.get('prize_product_id', None)
    if not prize_product_id:
        return jsonify({"msg": "Bad input data. Need: prize_product_id"}), 400

    # If no product_id provided, get all costomer who made order
    product_id = data.get('product_id', None)
    if product_id:
        filter_product_id = FBCampaignOrder.product_id == product_id
    else:
        filter_product_id = FBCampaignOrder.product_id != None

    num_of_winner = data.get('num_of_winner', 1)

    try:
        fb_campaign_orders = FBCampaignOrder.query.filter(
            FBCampaignOrder.fb_campaign_id == fb_campaign_id,
            FBCampaignOrder.comment_id != 'luckydraw',
            filter_product_id
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    if not fb_campaign_orders:
        return jsonify({"msg": "Campaign order not found."}), 404

    # Initialize lucky draw event data
    candidate_set = set()
    winner_list = []
    order_code = ""

    # Get the candidate set and order code
    for fb_campaign_order in fb_campaign_orders:
        candidate_set.add(fb_campaign_order.fb_user_id)
    if product_id:
        order_code = orm_get_fb_campaign_product(
            fb_campaign_id, product_id).order_code

    # Handles the situation where the requested number of winners is too large
    if num_of_winner > len(candidate_set):
        num_of_winner = len(candidate_set)

    # If the number_of_winners is invalid to sample(), return empty list
    try:
        winner_list = random.sample(candidate_set, num_of_winner)
    except:
        winner_list = []

    # Create new lucky draw event
    try:
        fb_campaign_lucky_draw = FBLuckyDraw(
            fb_campaign_id=fb_campaign_id,
            product_id=product_id,
            order_code=order_code,
            prize_product_id=prize_product_id,
            num_of_winner=num_of_winner,
            candidate_set=json.dumps(list(candidate_set)),
            winner_list=json.dumps(winner_list)
        )
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object init failed."}), 500
    try:
        db.session.add(fb_campaign_lucky_draw)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query ADD failed."}), 500

    for winner_fb_user_id in winner_list:
        fb_campaign_order = orm_get_fb_campaign_orders(
            fb_campaign_id, product_id, winner_fb_user_id)
        prize_product = orm_get_fb_campaign_product(
            fb_campaign_id, prize_product_id)
        orm_create_fb_campaign_order(fb_campaign_id, prize_product_id, fb_campaign_order.fb_user_id, fb_campaign_order.fb_user_name,
                                     1, prize_product.order_code, 'lucky_draw', 'lucky_draw_from_order',
                                     utc_now_timestamp(), 'valid')

        comment_on_campaign_congrats_lucky_draw_winner(
            fb_campaign_id, winner_fb_user_id, prize_product_id)

    fb_lucky_draw_schema = FBLuckyDrawSchema()
    return fb_lucky_draw_schema.jsonify(fb_campaign_lucky_draw), 201


@ connex_app.route("/fb_campaign/lucky_draw/comment/<fb_campaign_id>", methods=['POST'])
# @jwt_required
def create_fb_campaign_lucky_draw_comment(fb_campaign_id):
    data = request.get_json()
    # If there's no data provided
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    prize_product_id = data.get('prize_product_id', None)
    if not prize_product_id:
        return jsonify({"msg": "Bad input data. Need: prize_product_id"}), 400

    keyword = data.get('keyword', "")
    num_of_winner = data.get('num_of_winner', 1)

    fb_campaign = orm_get_fb_campaign(fb_campaign_id)
    if not fb_campaign:
        return jsonify({"msg": "FB Campaign not found."}), 404

    try:
        fb_campaign_comments = FBCampaignComment.query.filter(
            FBCampaignComment.fb_campaign_id == fb_campaign_id,
            FBCampaignComment.message.contains(keyword),
            FBCampaignComment.fb_user_id != fb_campaign.fb_page_id
        ).with_entities(FBCampaignComment.fb_user_id).distinct().all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    if not fb_campaign_comments:
        return jsonify({"msg": "Campaign comment not found."}), 404

    # Initialize lucky draw event data
    candidate_set = set()
    winner_list = []
    order_code = ""

    # Get the candidate set and order code
    for fb_campaign_comment in fb_campaign_comments:
        candidate_set.add(fb_campaign_comment.fb_user_id)
    order_code = keyword

    # Handles the situation where the requested number of winners is too large
    if num_of_winner > len(candidate_set):
        num_of_winner = len(candidate_set)

    # If the number_of_winners is invalid to sample(), return empty list
    try:
        winner_list = random.sample(candidate_set, num_of_winner)
    except:
        winner_list = []

    # Create new lucky draw event
    try:
        fb_campaign_lucky_draw = FBLuckyDraw(
            fb_campaign_id=fb_campaign_id,
            product_id=0,
            order_code=order_code,
            prize_product_id=prize_product_id,
            num_of_winner=num_of_winner,
            candidate_set=json.dumps(list(candidate_set)),
            winner_list=json.dumps(winner_list)
        )
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object init failed."}), 500
    try:
        db.session.add(fb_campaign_lucky_draw)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query ADD failed."}), 500

    for winner_fb_user_id in winner_list:
        fb_campaign_comment = orm_get_fb_campaign_comment_by_fb_user_id(
            winner_fb_user_id)
        prize_product = orm_get_fb_campaign_product(
            fb_campaign_id, prize_product_id)
        orm_create_fb_campaign_order(fb_campaign_id, prize_product_id, fb_campaign_comment.fb_user_id, fb_campaign_comment.fb_user_name,
                                     1, prize_product.order_code, 'lucky_draw', 'lucky_draw_from_comment',
                                     utc_now_timestamp(), 'valid')

        comment_on_campaign_congrats_lucky_draw_winner(
            fb_campaign_id, winner_fb_user_id, prize_product_id)

    fb_lucky_draw_schema = FBLuckyDrawSchema()
    return fb_lucky_draw_schema.jsonify(fb_campaign_lucky_draw), 201


@ connex_app.route("/fb_campaign/lucky_draw/like/<fb_campaign_id>", methods=['POST'])
# @jwt_required
def create_fb_campaign_lucky_draw_like(fb_campaign_id):
    fb_campaign = orm_get_fb_campaign(fb_campaign_id)
    if not fb_campaign:
        return jsonify({"msg": "FB Campaign not found."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    prize_product_id = data.get('prize_product_id', None)
    if not prize_product_id:
        return jsonify({"msg": "Bad input data. Need: prize_product_id"}), 400

    num_of_winner = data.get('num_of_winner', 1)

    fb_page = orm_get_fb_page_of_fb_campaign_id(fb_campaign.fb_campaign_id)
    if not fb_page:
        return {"campaign id": fb_campaign.fb_campaign_id, "error": 'fb_page not found'}

    # Initialize lucky draw event data
    candidate_set = set()
    winner_list = []
    order_code = "fb_likes"

    try:
        response = fb_api_get_likes(
            fb_page.fb_page_token, fb_campaign.fb_post_id, params={"limit": "5"})
        for person in response['data']:
            candidate_set.add((person['id'], person['name']))
        while True:
            try:
                response = fb_api_get_likes(
                    fb_page.fb_page_token, fb_campaign.fb_post_id, params={"limit": "5", "after": response['paging']['cursors']['after']})
                for person in response['data']:
                    candidate_set.add((person['id'], person['name']))
            except:
                break
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": response}), 500

    # Handles the situation where the requested number of winners is too large
    if num_of_winner > len(candidate_set):
        num_of_winner = len(candidate_set)

    # If the number_of_winners is invalid to sample(), return empty list
    try:
        winner_list = random.sample(candidate_set, num_of_winner)
    except:
        winner_list = []

    # Create new lucky draw event
    try:
        fb_campaign_lucky_draw = FBLuckyDraw(
            fb_campaign_id=fb_campaign_id,
            product_id=0,
            order_code=order_code,
            prize_product_id=prize_product_id,
            num_of_winner=num_of_winner,
            candidate_set=json.dumps(list(candidate_set)),
            winner_list=json.dumps(winner_list)
        )
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object init failed."}), 500
    try:
        db.session.add(fb_campaign_lucky_draw)
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query ADD failed."}), 500

    for winner_fb_user in winner_list:
        prize_product = orm_get_fb_campaign_product(
            fb_campaign_id, prize_product_id)
        orm_create_fb_campaign_order(fb_campaign_id, prize_product_id, winner_fb_user[0], winner_fb_user[1],
                                     1, prize_product.order_code, 'lucky_draw', 'lucky_draw_from_like',
                                     utc_now_timestamp(), 'valid')
        # TODO testing
        comment_on_campaign_congrats_lucky_draw_winner(
            fb_campaign_id, winner_fb_user[1], prize_product_id)

    fb_lucky_draw_schema = FBLuckyDrawSchema()
    return fb_lucky_draw_schema.jsonify(fb_campaign_lucky_draw), 201


@ connex_app.route("/fb_campaign/lucky_draw/<fb_campaign_id>", methods=['GET'])
# @jwt_required
def get_fb_campaign_lucky_draws(fb_campaign_id):
    # Handles the parameters fb_lucky_draw_id
    fb_lucky_draw_id = request.args.get('fb_lucky_draw_id', None)
    if fb_lucky_draw_id:
        filter_fb_lucky_draw_id = FBLuckyDraw.fb_lucky_draw_id == fb_lucky_draw_id
    else:
        filter_fb_lucky_draw_id = FBLuckyDraw.fb_lucky_draw_id != None

    # Handles the parameters product_id
    product_id = request.args.get('product_id', None)
    if product_id:
        filter_product_id = FBLuckyDraw.product_id == product_id
    else:
        filter_product_id = FBLuckyDraw.product_id != None

    # Handles the parameters order_code
    order_code = request.args.get('order_code', None)
    if order_code:
        filter_order_code = FBLuckyDraw.order_code == order_code
    else:
        filter_order_code = FBLuckyDraw.order_code != None

    try:
        fb_campaign_lucky_draws = FBLuckyDraw.query.filter(
            FBLuckyDraw.fb_campaign_id == fb_campaign_id,
            filter_fb_lucky_draw_id,
            filter_product_id,
            filter_order_code
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not fb_campaign_lucky_draws:
        return jsonify({"msg": "Campaign lucky draw not found."}), 404

    fb_lucky_draw_schema = FBLuckyDrawSchema(many=True)
    return fb_lucky_draw_schema.jsonify(fb_campaign_lucky_draws), 200


@ connex_app.route("/fb_campaign/lucky_draw/<fb_campaign_id>", methods=['DELETE'])
# @jwt_required
def delete_fb_campaign_lucky_draw(fb_campaign_id):
    # Handles the parameters fb_lucky_draw_id
    fb_lucky_draw_id = request.args.get('fb_lucky_draw_id', None)
    if fb_lucky_draw_id:
        filter_fb_lucky_draw_id = FBLuckyDraw.fb_lucky_draw_id == fb_lucky_draw_id
    else:
        filter_fb_lucky_draw_id = FBLuckyDraw.fb_lucky_draw_id != None

    # Handles the parameters product_id
    product_id = request.args.get('product_id', None)
    if product_id:
        filter_product_id = FBLuckyDraw.product_id == product_id
    else:
        filter_product_id = FBLuckyDraw.product_id != None

    # Handles the parameters order_code
    order_code = request.args.get('order_code', None)
    if order_code:
        filter_order_code = FBLuckyDraw.order_code == order_code
    else:
        filter_order_code = FBLuckyDraw.order_code != None

    try:
        fb_campaign_lucky_draws = FBLuckyDraw.query.filter(
            FBLuckyDraw.fb_campaign_id == fb_campaign_id,
            filter_fb_lucky_draw_id,
            filter_product_id,
            filter_order_code
        ).all()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query GET failed."}), 500
    # Emtpy query result
    if not fb_campaign_lucky_draws:
        return jsonify({"msg": "FB Campaign Lucky Draw not found."}), 404

    # Stat for return
    num_of_deletion = len(fb_campaign_lucky_draws)

    try:
        for fb_campaign_lucky_draw in fb_campaign_lucky_draws:
            db.session.delete(fb_campaign_lucky_draw)
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB object delete failed."}), 500
    try:
        db.session.commit()
    except:
        logger.error(traceback.format_exc())
        return jsonify({"msg": "DB query DELETE failed."}), 500

    return jsonify({"Number of deletion": num_of_deletion}), 200
