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

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.type != "customer":
                return Response("trying to login user type User", status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.create(
                name=facebook_name, email=email, type="customer")
        user.facebook_info["id"] = facebook_id
        user.facebook_info["name"] = facebook_name
        user.facebook_info["picture"] = picture
        user.save()

        if AuthUser.objects.filter(email=email).exists():
            auth_user = AuthUser.objects.get(email=email)
        else:
            auth_user = AuthUser.objects.create_user(
                facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))

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

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.type != "user":
                return Response("trying to login customer type User", status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.create(
                name=facebook_name, email=email, type="user")
        user.facebook_info["id"] = facebook_id
        user.facebook_info["name"] = facebook_name
        user.facebook_info["picture"] = picture
        user.save()

        if AuthUser.objects.filter(email=email).exists():
            auth_user = AuthUser.objects.get(email=email)
        else:
            auth_user = AuthUser.objects.create_user(
                facebook_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))

        auth_user.last_login = datetime.now()
        auth_user.save()
        refresh = RefreshToken.for_user(auth_user)

        ret = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response(ret, status=status.HTTP_200_OK)
