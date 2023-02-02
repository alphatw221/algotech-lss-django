from django.http import HttpResponse, HttpResponseRedirect

from django.conf import settings
from rest_framework.decorators import api_view

from api import models
import lib
import service
import json



@api_view(['GET', 'POST'])
def oauth_redirect(request):
    try:
        if request.method == 'GET':
            
            print(request.META)
            code = request.query_params.get('code')
            state = request.query_params.get('state')
            print(state)
            state = json.loads(state)
            redirect_to = state.get('redirect_to')
            redirect_uri = state.get('redirect_uri')
            print(redirect_uri)
            platform = state.get('platform')
            role = state.get('role')
            response = HttpResponseRedirect(redirect_to=redirect_to)

            if platform == 'facebook':
                # protocol = request.META['wsgi.url_scheme']    
                # domain = request.META['HTTP_HOST']
                # path = request.META['PATH_INFO']

                # full_path = protocol + "://" + domain + path
                code,res = service.facebook.user.get_long_lived_token(code, redirect_uri)
                
                if code==200:
                    facebook_token = res.get('access_token')
                    lss_token = lib.helper.login_helper.FacebookLogin.get_token(facebook_token,user_type='customer')
                    response.set_cookie('access_token',lss_token.get('access'))
                    response.set_cookie('login_with', platform)
            
            # return
            return response





        elif request.method == 'POST':
            
            print(request)

            response = HttpResponseRedirect(
                redirect_to='https://www.google.com')
            # response.set_cookie('access_token',token.get('access'))
            return response

                
    except Exception:
            import traceback
            print(traceback.format_exc())
            return HttpResponse(status=400)
# {'REQUEST_METHOD': 'GET', 'QUERY_STRING': 'code=AQBasejBoteU4N2eqcUkDClJx6oufkO9ifMtKbcbqWxHBMBYC7y6RkvbsLVYjF_tv5ZxToRGvKi8gni1QDFzLAmAvuUJmfajD3-c8nHyPTpukBCOcsBhISPqsRGxGVfJe4FyrId8cLNM3kD8XvPFbHMeaSPKVW_76ELfYN6mLpp6Jo1ce-cHPIdkFFzPRGCsPYN3hyumiIL8IvE6X6qbMOyg2cwihZGOrDBAuw6p1qUdBTAVG3ueCaBTY5MtrjgoYBFHRAeaL5pntrXKtVTLKR6EmXXmzS7kZ3WQWTx96YCntS591Wy_mhurnj7enAWsHH8VDE504fK9hpaJb3lRpNNBEELVFTaLvHEckWAZoPmFF0VdwTrasDE17FodbhsoGyg&state=%7B%22redirect_to%22%3A%22https%3A%2F%2Flocalhost%3A3000%2Fbuyer%2Fcart%2F63d8c1c09a8bff4d162e6f0a%22%2C%22platform%22%3A%22facebook%22%7D', 'SCRIPT_NAME': '', 'PATH_INFO': '/oauth/redirect/', 'wsgi.multithread': True, 'wsgi.multiprocess': True, 'REMOTE_ADDR': '127.0.0.1', 'REMOTE_HOST': '127.0.0.1', 'REMOTE_PORT': 49998, 'SERVER_NAME': '127.0.0.1', 'SERVER_PORT': '8000', 'HTTP_HOST': 'localhost:8000', 'HTTP_CONNECTION': 'keep-alive', 'HTTP_PRAGMA': 'no-cache', 'HTTP_CACHE_CONTROL': 'no-cache', 'HTTP_SEC_CH_UA': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"', 'HTTP_SEC_CH_UA_MOBILE': '?0', 'HTTP_SEC_CH_UA_PLATFORM': '"macOS"', 'HTTP_UPGRADE_INSECURE_REQUESTS': '1', 'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36', 'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'HTTP_SEC_FETCH_SITE': 'none', 'HTTP_SEC_FETCH_MODE': 'navigate', 'HTTP_SEC_FETCH_USER': '?1', 'HTTP_SEC_FETCH_DEST': 'document', 'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br', 'HTTP_ACCEPT_LANGUAGE': 'zh-TW,zh;q=0.9', 'HTTP_COOKIE': 'login_with=anonymousUser'}