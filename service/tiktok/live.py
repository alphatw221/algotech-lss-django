from ._tk_api_caller import load_response, DEFAULT_CLIENT_PARAMS, DEFAULT_REQUEST_HEADERS, TIKTOK_URL_WEBCAST
from requests import request
import urllib

def send_message(text, room_id, session_id, sign_url=None):
    url = TIKTOK_URL_WEBCAST+"room/chat/"
    params = {**DEFAULT_CLIENT_PARAMS, "content": text, 'room_id':room_id}
    # params = { "content": text}
    header = DEFAULT_REQUEST_HEADERS

    # url = update_url(url, params)
    # print(url)
    # print(params)
    response = request(
        "POST",
        url, 
        headers = header, 
        
        cookies={'sessionid':session_id},
        json = params,
        timeout=5
    )
    return load_response(response)





def update_url( url: str, params: dict) -> str:
    """
    Update a URL with given parameters by breaking it into components, adding new ones, and rebuilding it
    :param url: The URL we are updating
    :param params: The parameters to update it with
    :return: The updated URL
    """

    parsed = list(urllib.parse.urlparse(url))
    query = {**params, **dict(urllib.parse.parse_qsl(parsed[4]))}
    parsed[4] = urllib.parse.urlencode(query)
    return urllib.parse.urlunparse(parsed)