from api.utils.api.facebook._fb_api_caller import FacebookApiCaller


def api_fb_get_me(token: str):
    ret = FacebookApiCaller('me', bearer_token=token).get()
    return ret


def api_fb_get_id(token: str, user_or_page_id: str):
    ret = FacebookApiCaller(user_or_page_id, bearer_token=token).get()
    return ret


def api_fb_get_accounts_from_user(user_token: str, user_id: str):
    ret = FacebookApiCaller(f'{user_id}/accounts',
                            bearer_token=user_token,).get()
    return ret


def api_fb_get_page_token_from_user(user_token: str, page_id: str):
    ret = FacebookApiCaller(page_id, bearer_token=user_token,
                            params={"fields": "access_token"}).get()
    return ret
