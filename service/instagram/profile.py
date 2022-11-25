from ..facebook._fb_api_caller import FacebookApiCaller


def get_profile_info(page_token: str, profile_id: str):
    params = {
        "fields": "id,name,profile_picture_url"
    }
    ret = FacebookApiCaller(f'v13.0/{profile_id}', bearer_token=page_token,
                            params=params).get()
    return ret


def get_profile_live_media(page_token: str, profile_id: str, limit:int=100):
    params = {
        "fields": "id,media_url,username,timestamp",
        "limit": limit
    }
    ret = FacebookApiCaller(f'v13.0/{profile_id}/live_media', bearer_token=page_token,
                            params=params).get()
    return ret

def get_profile_media(page_token: str, profile_id: str, limit:int=100):
    params = {
        "fields": "id,media_url,username,timestamp,caption",
        "limit": limit
    }
    ret = FacebookApiCaller(f'v13.0/{profile_id}/media', bearer_token=page_token,
                            params=params).get()
    return ret
