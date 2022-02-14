from datetime import datetime
import string
import random

import requests
from django.http import HttpResponse

from api.models.campaign.campaign import Campaign
from api.models.user.user import User
from django.contrib.auth.models import User as AuthUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from api.utils.common.verify import ApiVerifyError
from backend.api.facebook.user import api_fb_get_me_login
from backend.api.google.user import api_google_get_token, api_google_get_userinfo
from lss.views.custom_jwt import CustomTokenObtainPairSerializer
from backend.api.instagram.user import *

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
        api_user = User.objects.get(email=email, type=user_type)
        auth_user = api_user.auth_user
    elif scenario2:
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

def google_fast_login_helper(request):
    code = request.GET.get("code")
    campaign_id = request.GET.get("state")

    response = requests.post(
        url="https://accounts.google.com/o/oauth2/token",
        data={
            "code": code,
            "client_id": "536277208137-okgj3vg6tskek5eg6r62jis5didrhfc3.apps.googleusercontent.com",
            "client_secret": "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",
            "redirect_uri": settings.GCP_API_LOADBALANCER_URL + "/api/user/google_user_callback",
            "grant_type": "authorization_code"
        }
    )
    # code, response = api_google_post_token(code, "http://localhost:8001" + "/api/user/google_user_callback")
    if not response.status_code / 100 == 2:
        return HttpResponse(f"NOT OK")
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_token")
    campaign_object = Campaign.objects.get(id=campaign_id)
    campaign_object.youtube_campaign["access_token"] = access_token
    campaign_object.youtube_campaign["refresh_token"] = refresh_token
    campaign_object.save()
    print(response.json())
    return HttpResponse(f"OK")

def google_login_helper(request, user_type='customer'):

    code = request.GET.get("code")

    response = requests.post(
        url="https://accounts.google.com/o/oauth2/token",
        data={
            "code": code,
            "client_id": "536277208137-okgj3vg6tskek5eg6r62jis5didrhfc3.apps.googleusercontent.com",
            "client_secret": "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",
            "redirect_uri": settings.GCP_API_LOADBALANCER_URL + "/api/user/google_user_login_callback",
            "grant_type": "authorization_code"
        }
    )
    if not response.status_code / 100 == 2:
        return HttpResponse(f"NOT OK")
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_toekn")

    code, response = api_google_get_userinfo(access_token)

    if response.status_code / 100 != 2:
        raise ApiVerifyError("google user token invalid")

    google_id = response["id"]
    google_name = response["name"]
    google_picture = response["picture"]
    email = response["email"]

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

    if user_type=='user' and api_user.status != 'valid':
        raise ApiVerifyError('account not activated')

    api_user.google_info["access_token"] = access_token
    api_user.google_info['refresh_token'] = refresh_token
    api_user.google_info["id"] = google_id
    api_user.google_info["name"] = google_name
    api_user.google_info["picture"] = google_picture
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