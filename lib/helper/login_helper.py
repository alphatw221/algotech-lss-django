from django.contrib.auth.models import User as AuthUser
from rest_framework.response import Response
from rest_framework import status

from api import models
from api.utils.error_handle.error.api_error import ApiCallerError, ApiVerifyError

from lss.views.custom_jwt import CustomTokenObtainPairSerializer
from backend.api.facebook.user import api_fb_get_me_login

from datetime import datetime
import random
import string

class GeneralLogin():

    @classmethod
    def get_token(cls, email, password):
        
        if not AuthUser.objects.filter(email=email).exists():
            return Response({"message": "email or password incorrect"}, status=status.HTTP_401_UNAUTHORIZED)

        auth_user = AuthUser.objects.get(email=email)

        if not auth_user.check_password(password):
            return Response({"message": "email or password incorrect"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class FacebookLogin():

    @classmethod
    def get_token(cls, token, user_type):
        status_code, response = api_fb_get_me_login(token)
        if status_code / 100 != 2:
            raise ApiVerifyError("facebook user token invalid")
            
        facebook_id = response.get('id')
        facebook_name = response.get('name')
        facebook_picture = response.get('picture',{}).get('data',{}).get('url')
        email = response.get('email')

        if not email:
            raise ApiVerifyError("can't get email from facebook")

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
                facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
            api_user.auth_user = auth_user
        elif scenario3:
            auth_user = AuthUser.objects.get(email=email)
            api_user = models.user.user.User.objects.create(
                name=facebook_name, email=email, type=user_type, status='new', auth_user=auth_user)
        else:  # scenario4
            auth_user = AuthUser.objects.create_user(
                facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
            api_user = models.user.user.User.objects.create(
                name=facebook_name, email=email, type=user_type, status='new', auth_user=auth_user)

        if user_type == 'user' and api_user.status != 'valid':
            raise ApiVerifyError('account not activated')

        api_user.facebook_info["token"] = token
        api_user.facebook_info["id"] = facebook_id
        api_user.facebook_info["name"] = facebook_name
        api_user.facebook_info["picture"] = facebook_picture
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
    def get_token(cls, code):
        pass




# def _