from ._rebrandly_api_caller import get_headers, load_response, domain_url

import requests

def create_link( destination, slashtag = None, title=''):

    headers = get_headers()
    data = {
        'destination':destination,
        'slashtag':slashtag,
        'title':title,
        'domain':{
                "id": "54f90b1d4cf6410db2f1ab73dd5793ec",               #lss.tw
                "ref": "/domains/54f90b1d4cf6410db2f1ab73dd5793ec"      #lss.tw
            },
    }

    res = requests.post(domain_url+'/v1/links', headers=headers, json=data, timeout=5)

    return load_response(res)