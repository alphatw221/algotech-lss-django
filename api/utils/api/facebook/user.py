from api.utils.api.facebook._fb_api_caller import FacebookApiCaller


def api_fb_me(token):
    caller = FacebookApiCaller(bearer_token=token)
    print(caller.get('me'))
