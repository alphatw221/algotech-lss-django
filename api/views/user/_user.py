from datetime import datetime
import string
import random
from api.models.user.user import User
from django.contrib.auth.models import User as AuthUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status


def customer_login_helper(self, request, pk=None):

    facebook_user_token = request.data.get('accessToken')
    facebook_id = request.data.get('id')
    facebook_name = request.data.get('name')
    facebook_picture = request.data.get('picture')
    email = request.data.get('email')

    api_user_exists = User.objects.filter(
        email=email, type='customer').exists()
    auth_user_exists = AuthUser.objects.filter(email=email).exists()

    scenario1 = api_user_exists and auth_user_exists
    scenario2 = api_user_exists and not auth_user_exists
    scenario3 = not api_user_exists and auth_user_exists
    # scenario4: both don't exists
    if scenario1:
        api_user = User.objects.get(email=email, type='customer')
        auth_user = api_user.auth_user
    elif scenario2:
        api_user = User.objects.get(email=email, type='customer')
        auth_user = AuthUser.objects.create_user(
            facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        api_user.auth_user = auth_user
    elif scenario3:
        auth_user = AuthUser.objects.get(email=email)
        api_user = User.objects.create(
            name=facebook_name, email=email, type='customer', auth_user=auth_user)
    else:  # scenario4
        auth_user = AuthUser.objects.create_user(
            facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        api_user = User.objects.create(
            name=facebook_name, email=email, type='customer', auth_user=auth_user)

    api_user.facebook_info["token"] = facebook_user_token
    api_user.facebook_info["id"] = facebook_id
    api_user.facebook_info["name"] = facebook_name
    api_user.facebook_info["picture"] = facebook_picture
    api_user.save()

    auth_user.last_login = datetime.now()
    auth_user.save()

    refresh = RefreshToken.for_user(auth_user)

    ret = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

    return Response(ret, status=status.HTTP_200_OK)


def seller_login_helper(self, request, pk=None):

    facebook_user_token = request.data.get('accessToken')
    facebook_id = request.data.get('id')
    facebook_name = request.data.get('name')
    facebook_picture = request.data.get('picture')
    email = request.data.get('email')

    api_user_exists = User.objects.filter(
        email=email, type='user').exists()
    auth_user_exists = AuthUser.objects.filter(email=email).exists()

    scenario1 = api_user_exists and auth_user_exists
    scenario2 = api_user_exists and not auth_user_exists
    scenario3 = not api_user_exists and auth_user_exists
    # scenario4: both don't exists
    if scenario1:
        api_user = User.objects.get(email=email, type='user')
        auth_user = api_user.auth_user
    elif scenario2:
        api_user = User.objects.get(email=email, type='user')
        auth_user = AuthUser.objects.create_user(
            facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        api_user.auth_user = auth_user
    elif scenario3:
        auth_user = AuthUser.objects.get(email=email)
        api_user = User.objects.create(
            name=facebook_name, email=email, type='user', status='new', auth_user=auth_user)
    else:  # scenario4
        auth_user = AuthUser.objects.create_user(
            facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
        api_user = User.objects.create(
            name=facebook_name, email=email, type='user', status='new', auth_user=auth_user)

    print(api_user.status)
    if api_user.status != 'valid':
        return Response({"message": "account not activated"}, status=status.HTTP_401_UNAUTHORIZED)

    api_user.facebook_info["token"] = facebook_user_token
    api_user.facebook_info["id"] = facebook_id
    api_user.facebook_info["name"] = facebook_name
    api_user.facebook_info["picture"] = facebook_picture
    api_user.save()

    auth_user.last_login = datetime.now()
    auth_user.save()

    refresh = RefreshToken.for_user(auth_user)

    ret = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

    return Response(ret, status=status.HTTP_200_OK)
