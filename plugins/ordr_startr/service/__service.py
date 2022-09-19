import json

def load_response(response):
    data = json.loads(response.text)
    print(response.status_code)
    if not int(response.status_code / 100 )== 2 :
        return False, data
    return True, data

def get_header(key):
    return {
        'Content-Type': 'application/json',
        'Authorization':f'key {key}',
        'Cookie':'connect.sid=s%3AYL50XGi9b8BAy7GBuuduq_uwU8ppmgMq.25FGPwhdtTR1uchnIRAFd6Z7CHU9R57EhBa5x1IDW6I' 

    }

platform_source_type_map = {'facebook':'FB', 'instagram':'IG', 'youtube':'YT', 'twitch':'TW', 'tiktok':'TT'}