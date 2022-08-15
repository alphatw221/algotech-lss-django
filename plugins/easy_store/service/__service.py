import json

def load_response(response):
    data = json.loads(response.text)
    if not response.status_code / 100 == 2 or 'error' in data:
        print(response.status_code)
        print(response.text)
        return False, None
    return True, data

def get_header(token):
    return {
        'Content-Type': 'application/json',
        'Easystore-Access-Token': token
    }