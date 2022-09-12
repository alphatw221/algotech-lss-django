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
        'X-Shopify-Access-Token': "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"
    }