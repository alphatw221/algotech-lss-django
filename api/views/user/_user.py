import traceback
from datetime import datetime
import string
import random
import requests
from django.http import HttpResponse, HttpResponseRedirect
from lss import settings
from api.models.campaign.campaign import Campaign
from api.models.user.user import User
from django.contrib.auth.models import User as AuthUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from api.utils.common.verify import  Verify
from api.utils.error_handle.error.api_error import ApiCallerError, ApiVerifyError
from backend.api.facebook.user import api_fb_get_me_login
from backend.api.google.user import api_google_get_userinfo
from backend.api.youtube.channel import api_youtube_get_list_channel_by_token
from backend.api.youtube.viedo import api_youtube_get_video_info_with_access_token
from lss.views.custom_jwt import CustomTokenObtainPairSerializer
from backend.api.instagram.user import *
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.shortcuts import redirect

def facebook_login_helper(request, user_type='user'):

    facebook_user_token = request.data.get('accessToken')
    status_code, response = api_fb_get_me_login(facebook_user_token)
    if status_code / 100 != 2:
        raise ApiVerifyError("facebook user token invalid")
        
    facebook_id = response['id']
    facebook_name = response['name']
    facebook_picture = response['picture']['data']['url']
    email = response['email']

    api_user_exists = User.objects.filter(
        email=email, type=user_type).exists()
    auth_user_exists = AuthUser.objects.filter(email=email).exists()


    scenario1 = api_user_exists and auth_user_exists
    scenario2 = api_user_exists and not auth_user_exists
    scenario3 = not api_user_exists and auth_user_exists

    # scenario4: both don't exists
    if scenario1:
        #TODO flaw fix
        api_user = User.objects.get(email=email, type=user_type)
        auth_user = api_user.auth_user
    elif scenario2:
        #TODO flaw fix
        api_user = User.objects.get(email=email, type=user_type)
        auth_user = AuthUser.objects.create_user(
            facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        api_user.auth_user = auth_user
    elif scenario3:
        auth_user = AuthUser.objects.get(email=email)
        api_user = User.objects.create(
            name=facebook_name, email=email, type=user_type, status='new', auth_user=auth_user)
    else:  # scenario4
        auth_user = AuthUser.objects.create_user(
            facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        api_user = User.objects.create(
            name=facebook_name, email=email, type=user_type, status='new', auth_user=auth_user)

    if user_type=='user' and api_user.status != 'valid':
        raise ApiVerifyError('account not activated')

    api_user.facebook_info["token"] = facebook_user_token
    api_user.facebook_info["id"] = facebook_id
    api_user.facebook_info["name"] = facebook_name
    api_user.facebook_info["picture"] = facebook_picture
    api_user.save()

    auth_user.last_login = datetime.now()
    auth_user.save()

    # refresh = RefreshToken.for_user(auth_user)

    refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

    ret = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

    return Response(ret, status=status.HTTP_200_OK)


def google_authorize_helper(request, user_type="seller"):

    def get_params(request):
        code = request.GET.get("code")
        campaign_id, youtube_video_id, redirect_uri = request.GET.get("state").split(",")
        print("campaign_id", campaign_id)
        print("youtube_video_id", youtube_video_id)
        return code, campaign_id, youtube_video_id, redirect_uri

    def api_google_post_token(code, redirect_uri):
        token_response = requests.post(
            url="https://accounts.google.com/o/oauth2/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            }
        )
        if not token_response.status_code / 100 == 2:
            raise ApiCallerError('get google token by code error')

        access_token = token_response.json().get("access_token")
        refresh_token = token_response.json().get("refresh_token")
        return access_token, refresh_token

    def get_user_youtube_channel_id(access_token, youtube_video_id):
        code, youtube_api_response = api_youtube_get_video_info_with_access_token(access_token, youtube_video_id)
        if not code / 100 == 2:
            raise ApiCallerError('get youtube video info error')

        return youtube_api_response["items"][0]["snippet"]["channelId"]

    def get_self_all_channels(access_token):

        code, list_channel_response = api_youtube_get_list_channel_by_token(access_token)
        if not code / 100 == 2:
            raise ApiCallerError('list youtube channels error')

        return [item["id"] for item in list_channel_response.get("items")]

    try:
        code, campaign_id, youtube_video_id, redirect_uri = get_params(request)
        access_token, refresh_token = api_google_post_token(code, redirect_uri)
        channelId = get_user_youtube_channel_id(access_token, youtube_video_id)
        your_all_channels = get_self_all_channels(access_token)

        if channelId not in your_all_channels:
            return HttpResponse(f"This Youtube video doesn't belong to this account")

        campaign = Verify.get_campaign(campaign_id)
        campaign.youtube_campaign["live_video_id"] = youtube_video_id
        campaign.youtube_campaign["access_token"] = access_token
        campaign.youtube_campaign["refresh_token"] = refresh_token
        campaign.save()
        return HttpResponseRedirect(redirect_to=f'{settings.WEB_SERVER_URL}/campaign/edit/{campaign_id}')
    except Exception as e:
        print(traceback.format_exc())
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

def verify_google_user(response, user_type):
    google_id, google_name, google_picture, email = response["sub"], response["name"], response["picture"], response["email"]

    api_user_exists = User.objects.filter(
        email=email, type=user_type).exists()
    auth_user_exists = AuthUser.objects.filter(email=email).exists()

    scenario1 = api_user_exists and auth_user_exists
    scenario2 = api_user_exists and not auth_user_exists
    scenario3 = not api_user_exists and auth_user_exists

    # scenario4: both don't exists

    if scenario1:
        api_user = User.objects.get(email=email, type=user_type)
        auth_user = api_user.auth_user
    elif scenario2:
        api_user = User.objects.get(email=email, type=user_type)
        auth_user = AuthUser.objects.create_user(
            google_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        api_user.auth_user = auth_user
    elif scenario3:
        auth_user = AuthUser.objects.get(email=email)
        api_user = User.objects.create(
            name=google_name, email=email, type=user_type, status='new', auth_user=auth_user)
    else:  # scenario4
        auth_user = AuthUser.objects.create_user(
            google_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        api_user = User.objects.create(
            name=google_name, email=email, type=user_type, status='new', auth_user=auth_user)

    if user_type == 'user' and api_user.status != 'valid':
        raise ApiVerifyError('account not activated')

    api_user.google_info["id"] = google_id
    api_user.google_info["name"] = google_name
    api_user.google_info["picture"] = google_picture


    auth_user.last_login = datetime.now()
    auth_user.save()
    api_user.save()


    refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

    ret = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

    return ret

def google_login_helper(request, user_type='customer'):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        token = request.query_params.get("token", None)
        CLIENT_ID = settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)
        print(idinfo)
        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')
        our_jwt_tokens = verify_google_user(idinfo, user_type=user_type)
        return Response(our_jwt_tokens, status=status.HTTP_200_OK)

    except Exception as e:
        print(traceback.format_exc())
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# def google_login_helper(request, user_type='customer'):

#     google_code = request.query_params.get("code")
#     print("google_code", google_code)
    
#     response = requests.post(
#             url="https://accounts.google.com/o/oauth2/token",
#             data={
#                 "code": request.query_params.get("code"),
#                 "client_id": "536277208137-okgj3vg6tskek5eg6r62jis5didrhfc3.apps.googleusercontent.com",
#                 "client_secret": "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",
#                 # "redirect_uri": 'http://localhost:8000/google-redirect',
#                 "redirect_uri": settings.WEB_SERVER_URL + "/google-redirect",
#                 "grant_type": "authorization_code"
#             }
#         )


#     if not response.status_code / 100 == 2:
#         print(response.json())
#         raise ApiCallerError('get google token fail')

#     access_token = response.json().get("access_token")
#     refresh_token = response.json().get("refresh_token")

#     code, response = api_google_get_userinfo(access_token)

#     if code / 100 != 2:
#         print(response)
#         print(traceback.format_exc)
#         raise ApiCallerError("google user token invalid")

#     google_id, google_name, google_picture, email = response["id"], response["name"], response["picture"], response["email"]
#     # google_name = response["name"]
#     # google_picture = response["picture"]
#     # email = response["email"]

#     api_user_exists = User.objects.filter(
#         email=email, type=user_type).exists()
#     auth_user_exists = AuthUser.objects.filter(email=email).exists()

#     scenario1 = api_user_exists and auth_user_exists
#     scenario2 = api_user_exists and not auth_user_exists
#     scenario3 = not api_user_exists and auth_user_exists

#     # scenario4: both don't exists

#     if scenario1:
#         api_user = User.objects.get(email=email, type=user_type)
#         auth_user = api_user.auth_user
#     elif scenario2:
#         api_user = User.objects.get(email=email, type=user_type)
#         auth_user = AuthUser.objects.create_user(
#             google_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
#         api_user.auth_user = auth_user
#     elif scenario3:
#         auth_user = AuthUser.objects.get(email=email)
#         api_user = User.objects.create(
#             name=google_name, email=email, type=user_type, status='new', auth_user=auth_user)
#     else:  # scenario4
#         auth_user = AuthUser.objects.create_user(
#             google_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
#         api_user = User.objects.create(
#             name=google_name, email=email, type=user_type, status='new', auth_user=auth_user)

#     if user_type == 'user' and api_user.status != 'valid':
#         raise ApiVerifyError('account not activated')

#     api_user.google_info["access_token"] = access_token
#     api_user.google_info['refresh_token'] = refresh_token
#     api_user.google_info["id"] = google_id
#     api_user.google_info["name"] = google_name
#     api_user.google_info["picture"] = google_picture

    
#     code, list_channel_response = api_youtube_get_list_channel_by_token(access_token)
    
#     if code / 100 == 2:
#         channels = {}
#         try:
#             for item in list_channel_response.get("items"):
#                 channels[item['id']] = item
#             api_user.youtube_info['channels'] = channels
#         except:
#             print("this account doesn't have any channel.")
#             api_user.youtube_info['channels'] = {
#                 "message": "this account doesn't have any channel."
#             }

#     auth_user.last_login = datetime.now()
#     auth_user.save()
#     api_user.save()


#     refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

#     ret = {
#         'refresh': str(refresh),
#         'access': str(refresh.access_token),
#     }

#     return Response(ret, status=status.HTTP_200_OK)

    # # red.set_cookie('token', str(refresh.access_token)) #TODO setting domain, expired
    # red.set_cookie("access_token", str(refresh.access_token), path="/", domain=None, samesite=None, secure=False)
    # return red


def instagram_login_helper(request, user_type='customer'):
    instagram_user_token = request.data.get('accessToken')

    #//--------------------------------

    instagram_id = "response['id']"
    instagram_name = ""
    instagram_picture = ""
    email = ""

    # //-------------------------------
    api_user_exists = User.objects.filter(
        email=email, type=user_type).exists()
    auth_user_exists = AuthUser.objects.filter(email=email).exists()


    scenario1 = api_user_exists and auth_user_exists
    scenario2 = api_user_exists and not auth_user_exists
    scenario3 = not api_user_exists and auth_user_exists

    # scenario4: both don't exists

    if scenario1:
        api_user = User.objects.get(email=email, type=user_type)
        auth_user = api_user.auth_user
    elif scenario2:
        api_user = User.objects.get(email=email, type=user_type)
        auth_user = AuthUser.objects.create_user(
            instagram_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        api_user.auth_user = auth_user
    elif scenario3:
        auth_user = AuthUser.objects.get(email=email)
        api_user = User.objects.create(
            name=instagram_name, email=email, type=user_type, status='new', auth_user=auth_user)
    else:  # scenario4
        auth_user = AuthUser.objects.create_user(
            instagram_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        api_user = User.objects.create(
            name=instagram_name, email=email, type=user_type, status='new', auth_user=auth_user)

    if user_type=='user' and api_user.status != 'valid':
        raise ApiVerifyError('account not activated')

    api_user.instagram_info["token"] = instagram_user_token
    api_user.instagram_info["id"] = instagram_id
    api_user.instagram_info["name"] = instagram_name
    api_user.instagram_info["picture"] = instagram_picture
    api_user.save()

    auth_user.last_login = datetime.now()
    auth_user.save()

    # refresh = RefreshToken.for_user(auth_user)

    refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

    ret = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

    return Response(ret, status=status.HTTP_200_OK)