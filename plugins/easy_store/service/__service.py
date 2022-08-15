import json

def load_response(response):
    if not response.status_code / 100 == 2:
        print(response.text)
        return False, None
    return True, json.loads(response.text)