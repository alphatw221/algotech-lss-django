from re import sub
from tracemalloc import start
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from itsdangerous import Serializer
from numpy import require

from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser

from api import rule, models, utils

import stripe, pytz, lib, service, business_policy, json
from backend.pymongo.mongodb import db

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import database


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = models.user.static_assets.StaticAssets.objects.all()


    @action(detail=False, methods=['POST'], url_path=r'seller/upload', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_upload_animation(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        asset_type, = lib.util.getter.getparams(request, ('aset_type', ), with_user=False)

        if asset_type not in models.user.static_assets.TYPE_CHOICE:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid')

        file, = lib.util.getter.getdata(request, ("file", ), required=True)
        if not file:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid')

        file_name=str(datetime.utcnow().timestamp())+file.name.replace(" ","")
        file_path = f'user_subscription/{user_subscription.id}/{asset_type}'
        animation_url = lib.util.storage.upload_image(file_path, file_name, file)
        static_asset = models.user.static_assets.StaticAssets.objects.create(user_subscription=user_subscription, name=file.name, path=animation_url, type=asset_type)
        data = models.user.static_assets.StaticAssetsSerializer(static_asset).data
        return Response(data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'seller_list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_list_animation(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        asset_type,  = lib.util.getter.getparams(request, ('asset_type,'), with_user=False)
        if asset_type in models.user.static_assets.TYPE_CHOICE:
            static_assets = user_subscription.assets.filter(type=asset_type)
        
        return Response(models.user.static_assets.StaticAssetsSerializer(static_assets, many=True).data, status=status.HTTP_200_OK)