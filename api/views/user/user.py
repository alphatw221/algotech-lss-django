from datetime import datetime
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.models.user.user import User, UserSerializer

from rest_framework.decorators import action
from django.contrib.auth.models import User as AuthUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status

import string
import random


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsAdminUser)
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filterset_fields = []

    @action(detail=False, methods=['POST'], url_path=r'customer_login')
    def customer_login(self, request, pk=None):

        facebook_id = request.data.get('id')
        facebook_name = request.data.get('name')
        picture = request.data.get('picture')
        email = request.data.get('email')

        api_user_exists = User.objects.filter(
            email=email, type="customer").exists()
        auth_user_exists = AuthUser.objects.filter(email=email).exists()

        scenario1 = api_user_exists and auth_user_exists
        scenario2 = api_user_exists and not auth_user_exists
        scenario3 = not api_user_exists and auth_user_exists
        # scenario4: both don't exists
        if scenario1:
            api_user = User.objects.get(email=email, type="customer")
            auth_user = api_user.auth_user
        elif scenario2:
            api_user = User.objects.get(email=email, type="customer")
            auth_user = AuthUser.objects.create_user(
                facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
            api_user.auth_user = auth_user
        elif scenario3:
            auth_user = AuthUser.objects.get(email=email)
            api_user = User.objects.create(
                name=facebook_name, email=email, type="customer", auth_user=auth_user)
        else:  # scenario4
            auth_user = AuthUser.objects.create_user(
                facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
            api_user = User.objects.create(
                name=facebook_name, email=email, type="customer", auth_user=auth_user)

        api_user.facebook_info["id"] = facebook_id
        api_user.facebook_info["name"] = facebook_name
        api_user.facebook_info["picture"] = picture
        api_user.save()

        auth_user.last_login = datetime.now()
        auth_user.save()

        refresh = RefreshToken.for_user(auth_user)

        ret = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response(ret, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'user_login')
    def user_login(self, request, pk=None):

        facebook_id = request.data.get('id')
        facebook_name = request.data.get('name')
        picture = request.data.get('picture')
        email = request.data.get('email')

        api_user_exists = User.objects.filter(
            email=email, type="user").exists()
        auth_user_exists = AuthUser.objects.filter(email=email).exists()

        scenario1 = api_user_exists and auth_user_exists
        scenario2 = api_user_exists and not auth_user_exists
        scenario3 = not api_user_exists and auth_user_exists
        # scenario4: both don't exists
        if scenario1:
            api_user = User.objects.get(email=email, type="user")
            auth_user = api_user.auth_user
        elif scenario2:
            api_user = User.objects.get(email=email, type="user")
            auth_user = AuthUser.objects.create_user(
                facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
            api_user.auth_user = auth_user
        elif scenario3:
            auth_user = AuthUser.objects.get(email=email)
            api_user = User.objects.create(
                name=facebook_name, email=email, type="user", auth_user=auth_user)
        else:  # scenario4
            auth_user = AuthUser.objects.create_user(
                facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
            api_user = User.objects.create(
                name=facebook_name, email=email, type="user", auth_user=auth_user)

        api_user.facebook_info["id"] = facebook_id
        api_user.facebook_info["name"] = facebook_name
        api_user.facebook_info["picture"] = picture
        api_user.save()

        auth_user.last_login = datetime.now()
        auth_user.save()

        refresh = RefreshToken.for_user(auth_user)

        ret = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response(ret, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'bind_youtube_channel')
    def bind_youtube_channel(self, request, pk=None):

        api_user = request.user.api_users.get(type="user")
        items = request.data.get('items')
        youtube_info = api_user.youtube_info
        youtube_info['channel'] = 'test'
        print(youtube_info)

        print(api_user)
        return Response("ok", status=status.HTTP_200_OK)
