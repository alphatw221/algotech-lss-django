from datetime import datetime
import string
import random
from api.models.user.user import User
from django.contrib.auth.models import User as AuthUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from api.utils.common.verify import ApiVerifyError
from backend.api.facebook.user import api_fb_get_me_login
from lss.views.custom_jwt import CustomTokenObtainPairSerializer

def login_helper(request, user_type='user'):

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