from django.contrib.auth.models import User as AuthUser
from django.conf import settings

from api import models

from lss.views.custom_jwt import CustomTokenObtainPairSerializer

import lib
from datetime import datetime
import random
import string
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

import service

class GeneralLogin():

    @classmethod
    def get_token(cls, email, password):
        
        if not AuthUser.objects.filter(email=email).exists():
            return

        auth_user = AuthUser.objects.get(email=email)
        

        if auth_user.api_users.filter(type='user').exists():
            lib.util.marking_tool.NewUserMark.check_mark(auth_user.api_users.get(type='user'), save=True)

        if not auth_user.check_password(password):
            return

        refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_email': email
        }

class FacebookLogin():

    @classmethod
    def get_token(cls, token, user_type):
        status_code, response = service.facebook.user.get_me_login(token)
        if status_code / 100 != 2:
            lib.util.google_cloud_logging.ApiLogEntry.write_entry(str({'error':'get facebook me error', 'response':response}))
            raise lib.error_handle.error.api_error.ApiVerifyError("fb_user_token_invalid")
            
        facebook_id = response.get('id')
        facebook_name = response.get('name')
        facebook_picture = response.get('picture',{}).get('data',{}).get('url')
        email = response.get('email')

        if not email:
            email = facebook_id+'@facebook.fake'
            # lib.util.google_cloud_logging.ApiLogEntry.write_entry(str({'error':'facebook email invalid', 'facebook_name':facebook_name, 'response':response}))
            # raise lib.error_handle.error.api_error.ApiVerifyError("fb_user_token_invalid")

        auth_user, api_user = create_or_get_user(email, user_type, facebook_name)
        # if not email:
        #     raise lib.error_handle.error.api_error.ApiVerifyError("unable_get_fb_email")

        # api_user_exists = models.user.user.User.objects.filter(
        #     email=email, type=user_type).exists()
        # auth_user_exists = AuthUser.objects.filter(email=email).exists()

        # scenario1 = api_user_exists and auth_user_exists
        # scenario2 = api_user_exists and not auth_user_exists
        # scenario3 = not api_user_exists and auth_user_exists

        # # scenario4: both don't exists
        # if scenario1:
        #     api_user = models.user.user.User.objects.get(email=email, type=user_type)
        #     auth_user = AuthUser.objects.get(email=email)
        #     if not api_user.auth_user:
        #         api_user.auth_user=auth_user
        # elif scenario2:
        #     api_user = models.user.user.User.objects.get(email=email, type=user_type)
        #     auth_user = AuthUser.objects.create_user(
        #         facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        #     api_user.auth_user = auth_user
        # elif scenario3:
        #     auth_user = AuthUser.objects.get(email=email)
        #     api_user = models.user.user.User.objects.create(
        #         name=facebook_name, email=email, type=user_type, status='new', auth_user=auth_user)
        # else:  # scenario4
        #     auth_user = AuthUser.objects.create_user(
        #         facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        #     api_user = models.user.user.User.objects.create(
        #         name=facebook_name, email=email, type=user_type, status='new', auth_user=auth_user)

        if user_type == 'user' and api_user.status != 'valid':
            raise lib.error_handle.error.api_error.ApiVerifyError('helper.account_not_activated')

        api_user.facebook_info["token"] = token
        api_user.facebook_info["id"] = facebook_id
        api_user.facebook_info["name"] = facebook_name
        api_user.facebook_info["picture"] = facebook_picture
        lib.util.marking_tool.NewUserMark.check_mark(api_user)
        api_user.save()

        auth_user.last_login = datetime.now()
        auth_user.save()

        refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class GoogleLogin():

    @classmethod
    def get_token_v0(cls, token="", user_type='customer'):
        status_code, response = service.google.user.api_google_get_userinfo(token)

        if status_code / 100 != 2:
            raise lib.error_handle.error.api_error.ApiVerifyError("user_google_token_invalid")

        google_id, google_name, google_picture, email = response.get('id'),response.get('name'),response.get('picture'),response.get('email'),
        
        if not email:
            raise lib.error_handle.error.api_error.ApiVerifyError("user_google_token_invalid")
            
        auth_user, api_user = create_or_get_user(email, user_type='customer', user_name=google_name)
        

        api_user.google_info["id"] = google_id
        api_user.google_info["name"] = google_name
        api_user.google_info["picture"] = google_picture
        lib.util.marking_tool.NewUserMark.check_mark(api_user)
        auth_user.last_login = datetime.now()
        auth_user.save()
        api_user.save()

        refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @classmethod
    def get_token(cls, token="", user_type='customer'):
        # ValueError: Token has wrong audience 536277208137-okgj3vg6tskek5eg6r62jis5didrhfc3.apps.googleusercontent.com, expected one of ['647555482564-u2s769q2ve0b270gnmr5bpqdfmc9tphl.apps.googleusercontent.com']
        # GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER = "647555482564-u2s769q2ve0b270gnmr5bpqdfmc9tphl.apps.googleusercontent.com"      #temporarily     as v2 is on different domain
        # print(settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER)
        # print('testtest')
        identity_info = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER, clock_skew_in_seconds=5)

        google_id, google_name, google_picture, email = identity_info.get("sub"), identity_info.get("name"), identity_info.get("picture"), identity_info.get("email")
        
        auth_user, api_user = create_or_get_user(email, user_type=user_type, user_name=google_name)
        # api_user_exists = models.user.user.User.objects.filter(
        #     email=email, type=user_type).exists()
        # auth_user_exists = AuthUser.objects.filter(email=email).exists()

        # scenario1 = api_user_exists and auth_user_exists
        # scenario2 = api_user_exists and not auth_user_exists
        # scenario3 = not api_user_exists and auth_user_exists

        # # scenario4: both don't exists

        # if scenario1:
        #     api_user = models.user.user.User.objects.get(email=email, type=user_type)
        #     auth_user = AuthUser.objects.get(email=email)
        #     if not api_user.auth_user:
        #         api_user.auth_user=auth_user
        # elif scenario2:
        #     api_user = models.user.user.User.objects.get(email=email, type=user_type)
        #     auth_user = AuthUser.objects.create_user(
        #         google_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        #     api_user.auth_user = auth_user
        # elif scenario3:
        #     auth_user = AuthUser.objects.get(email=email)
        #     api_user = models.user.user.User.objects.create(
        #         name=google_name, email=email, type=user_type, status='new', auth_user=auth_user)
        # else:  # scenario4
        #     auth_user = AuthUser.objects.create_user(
        #         google_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        #     api_user = models.user.user.User.objects.create(
        #         name=google_name, email=email, type=user_type, status='new', auth_user=auth_user)

        if user_type == 'user' and api_user.status != 'valid':
            raise lib.error_handle.error.api_error.ApiVerifyError('helper.account_not_activated')

        api_user.google_info["id"] = google_id
        api_user.google_info["name"] = google_name
        api_user.google_info["picture"] = google_picture
        lib.util.marking_tool.NewUserMark.check_mark(api_user)
        auth_user.last_login = datetime.now()
        auth_user.save()
        api_user.save()

        refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class ToktokLogin():

    @classmethod
    def get_token(cls, code):
        

        return {
            'refresh': str(''),
            'access': str(''),
        }



def create_or_get_user(email, user_type, user_name="unknown", ):
    
    
    auth_user, auth_user_created = AuthUser.objects.get_or_create(email=email)
    if auth_user_created:
        auth_user.username = user_name
        auth_user.set_password(''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        auth_user.save()

    api_user, api_user_created = models.user.user.User.objects.get_or_create( email=email, type=user_type)
    
    if api_user_created:
        api_user.name=user_name
        api_user.status='new'
        api_user.auth_user = auth_user
        api_user.save()
    elif api_user.auth_user != auth_user:
        api_user.auth_user = auth_user
        api_user.save()

    return auth_user, api_user

    api_user_exists = models.user.user.User.objects.filter(
        email=email, type=user_type).exists()
    auth_user_exists = AuthUser.objects.filter(email=email).exists()
    

    scenario1 = api_user_exists and auth_user_exists
    scenario2 = api_user_exists and not auth_user_exists
    scenario3 = not api_user_exists and auth_user_exists

    # scenario4: both don't exists
    if scenario1:
        api_user = models.user.user.User.objects.get(email=email, type=user_type)
        auth_user = AuthUser.objects.get(email=email)
        if not api_user.auth_user:
            api_user.auth_user=auth_user
    elif scenario2:
        api_user = models.user.user.User.objects.get(email=email, type=user_type)
        auth_user = AuthUser.objects.create_user(
            user_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        api_user.auth_user = auth_user
    elif scenario3:
        auth_user = AuthUser.objects.get(email=email)
        api_user = models.user.user.User.objects.create(
            name=user_name, email=email, type=user_type, status='new', auth_user=auth_user)
    else:  # scenario4
        auth_user = AuthUser.objects.create_user(
            user_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        api_user = models.user.user.User.objects.create(
            name=user_name, email=email, type=user_type, status='new', auth_user=auth_user)

    return auth_user, api_user