import json

def load_response(response):
    data = json.loads(response.text)
    if not int(response.status_code / 100 )== 2 :
        return False, data
    return True, data

def get_header(key):
    return {
        'Content-Type': 'application/json',
        'Authorization':f'key {key}',
        'Cookie':'connect.sid=s%3AhZb3dTGG8XBUGVW1mQP-unVbg7E1V_lK.dqbneJMgVqa%2BvrCeWKzxvUcNd91JViu4hQXs7Qls%2FuA'  #temp
    }

platform_source_type_map = {'facebook':'FB', 'instagram':'IG', 'youtube':'YT', 'twitch':'twitch', 'tiktok':'tiktok'}