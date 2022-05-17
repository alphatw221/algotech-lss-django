from ..facebook._fb_api_caller import FacebookApiCaller


def get_profile_info(page_token: str, profile_id: str):
    params = {
        "fields": "id,name,profile_picture_url"
    }
    ret = FacebookApiCaller(f'v13.0/{profile_id}', bearer_token=page_token,
                            params=params).get()
    return ret


def get_profile_live_media(page_token: str, profile_id: str):
    params = {
        "fields": "live_media"
    }
    ret = FacebookApiCaller(f'v13.0/{profile_id}', bearer_token=page_token,
                            params=params).get()
    return ret
