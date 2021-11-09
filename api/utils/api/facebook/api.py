from django.conf import settings
from dataclasses import dataclass
from api.utils.api.api_caller import RestApiJsonCaller


@dataclass
class FacebookApiCaller(RestApiJsonCaller):
    doamin_url: str = settings.FACEBOOK_API_URL


# TODO: implement facebook api module
"""
# Get the header which contains given token and make it a valid for a bearer token format
def access_token_header(token):
    return {"Authorization": "Bearer " + token}


# Simple api call with token in the header
def api_get_requests(access_token, url, params={}):
    try:
        response_data = requests.get(
            url,
            headers=access_token_header(access_token),
            params=params)
    except:
        raise Exception(traceback.format_exc())
    return response_data.json()


# Input token and api endpoint url of fb, this will send and return the result of fb api calling
def fb_api_get_requests(access_token, api_url, params={}):
    try:
        response_data = requests.get(
            _default_fb_url_ + api_url,
            headers=access_token_header(access_token),
            params=params)
    except:
        raise Exception(traceback.format_exc())
    return response_data.json()


def fb_api_post_requests(access_token, api_url, data,  params={}):
    try:
        response_data = requests.post(
            _default_fb_url_ + api_url,
            headers=access_token_header(access_token),
            json=data,
            params=params)
    except:
        raise Exception(traceback.format_exc())
    return response_data.json()


def get_token_info(access_token, params={}):
    params['input_token'] = access_token

    return fb_api_get_requests(access_token, "  ", params)


def page_send_message(page_access_token, page_id, recipient_id, message_text, params={}):
    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    }

    return fb_api_post_requests(page_access_token, page_id + "/messages", data, params={})


def page_comment_on_post(page_access_token, post_id, message_text, params={}):
    data = {"message": message_text}

    ret = fb_api_post_requests(
        page_access_token, post_id + "/comments", data, params={})
    if 'error' in ret:
        logger.error(ret)


def reply_to_buyer_with_pm_and_comment(fb_page_token, fb_comment_id, comment_msg, pm_msg):
    # Check the config and send private reply to the buyer
    if enable_page_send_private_reply:
        ret = private_reply_on_comment(
            fb_page_token, fb_comment_id, pm_msg)
        if 'error' in ret:
            logger.error(ret)
    # Check the config and comment back to the buyer
    if enable_comment_on_comment:
        ret = comment_on_comment(fb_page_token, fb_comment_id, comment_msg)
        if 'error' in ret:
            logger.error(ret)


def reply_to_buyer_on_comment_keyword(fb_page_token, fb_comment_id, msg):
    if enable_comment_on_comment:
        ret = comment_on_comment(fb_page_token, fb_comment_id, msg)
        if 'error' in ret:
            logger.error(ret)


def reply_to_buyer_on_comment_keyword_order(fb_page_token, fb_comment_id, msg):
    if enable_page_send_private_reply:
        ret = private_reply_on_comment(fb_page_token, fb_comment_id, msg)
        if 'error' in ret:
            logger.error(ret)


def comment_on_comment(page_access_token, comment_id, message_text, params={}):
    data = {
        "message": message_text
    }

    return fb_api_post_requests(page_access_token, comment_id + "/comments", data, params={})


def private_reply_on_comment(page_access_token, comment_id, message_text, params={}):
    data = {
        "recipient": {
            "comment_id": comment_id
        },
        "message": {
            "text": message_text
        }
    }

    return fb_api_post_requests(page_access_token, "me/messages", data, params={})


def get_long_lived_token_from_short_lived_token(short_lived_token, params={}):
    try:
        fb_app = FBAppInfo.query.filter_by(app_type="page_main").first()
        if not fb_app:
            logger.error("Missing fb_app.")
            return None

        params["grant_type"] = "fb_exchange_token"
        params["client_id"] = fb_app.fb_app_id
        params["client_secret"] = fb_app.fb_app_secret
        params["fb_exchange_token"] = short_lived_token

        long_lived_token = fb_api_get_requests(
            "", "oauth/access_token", params)
    except:
        logger.error(traceback.format_exc())
        return None

    return long_lived_token


def get_page_token_from_user_token(user_token, page_id, params={}):
    return fb_api_get_requests(user_token, page_id, {"fields": "access_token"})


def fb_api_get_profile_from_token(page_token, params={}):
    response_data = fb_api_get_requests(page_token, "me", params)

    try:
        return response_data['name'], response_data['id']
    except:
        logger.error(traceback.format_exc())
        return response_data


# Get the page token list from given user
def fb_api_get_page_list_from_token(user_token, fb_user_id, params={}):
    response_data = fb_api_get_requests(
        user_token, fb_user_id + "/accounts", params)

    return response_data


def fb_api_get_posts(page_token, profile_id, params={"order": "reverse_chronological", "limit": "100"}, latest=False):
    response_data = fb_api_get_requests(
        page_token, profile_id + '/posts', params)

    posts_data = response_data['data']

    if latest:
        posts_data = posts_data[-1:]

    posts_content = {}
    for post in posts_data:
        posts_content[post['id']] = {'created_time': post['created_time']}

        if 'story' in post.keys():
            posts_content[post['id']]['story'] = post['story']
        if 'message' in post.keys():
            posts_content[post['id']]['message'] = post['message']

    return posts_content


def fb_api_get_comments(page_token, post_id, params={"order": "reverse_chronological", "limit": "100"}):
    response_data = ""
    try:
        response_data = fb_api_get_requests(
            page_token, post_id+'/comments', params)
    except:
        logger.error(traceback.format_exc())
        return response_data

    return response_data


def fb_api_get_likes(page_token, post_id, params={"limit": "100"}):
    response_data = ""
    try:
        response_data = fb_api_get_requests(
            page_token, post_id+'/likes', params)
    except:
        logger.error(traceback.format_exc())
        return response_data

    return response_data


def fb_api_get_comments_since(page_token, fb_post_id, since, params={}):
    response_data = ""

    params['order'] = "chronological"
    params['limit'] = "100"
    params['date_format'] = "U"
    params['since'] = since
    params['live_filter'] = 'no_filter'
    params['fields'] = 'created_time,from{picture,name,id},message,id'

    try:
        response_data = fb_api_get_requests(
            page_token, fb_post_id+'/comments', params)
    except:
        logger.error(traceback.format_exc())
        return response_data

    return response_data


def fb_api_get_psid(page_token, psid, params={}):
    response_data = ""
    try:
        response_data = fb_api_get_requests(
            page_token, psid, params)
    except:
        logger.error(traceback.format_exc())
        return response_data

    return response_data
"""
