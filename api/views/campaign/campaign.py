import json

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from api.models.campaign.campaign import Campaign, CampaignSerializer, CampaignSerializerRetreive, CampaignSerializerCreate
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime
from api.models.youtube.youtube_channel import YoutubeChannel
from api.utils.common.permission import PlatfomrIsCampaignOwner

from backend.pymongo.mongodb import db
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from api.utils.common.common import *
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
import requests

def verify_seller_request(api_user):
    Verify.verify_user(api_user)
    return True

def verify_request(api_user, platform_name, platform_id, campaign_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)

    if campaign_id:
        if not platform.campaigns.filter(id=campaign_id).exists():
            raise ApiVerifyError("no campaign found")
        campaign = platform.campaigns.get(id=campaign_id)
        return platform, campaign

    return platform


class CampaignPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


class CampaignViewSet(viewsets.ModelViewSet):
    
    queryset = Campaign.objects.all().order_by('id')
    serializer_class = CampaignSerializer
    filterset_fields = []
    pagination_class = CampaignPagination

    @action(detail=True, methods=['GET'], url_path=r'retrieve_campaign', permission_classes=(IsAuthenticated, PlatfomrIsCampaignOwner,))
    @api_error_handler
    def retrieve_campaign(self, request, pk=None):
        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')
        api_user = request.user.api_users.get(type='user')
        campaign = Verify.get_campaign(campaign_id=pk)
        serializer = CampaignSerializerRetreive(campaign)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'retrieve_campaign_buyer')
    @api_error_handler
    def retrieve_campaign_buyer(self, request, pk=None):
        campaign_data = db.api_campaign.find_one({'id': int(pk)})
        campaign_data.pop('_id', None)
        print (campaign_data)
        # serializer = Campaign.objects.get(id=pk)

        return Response(campaign_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list_campaign', permission_classes=(IsAuthenticated, PlatfomrIsCampaignOwner,))
    @api_error_handler
    def list_campaign(self, request):
        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')
        order_by = request.query_params.get('order_by')
        campaign_status = request.query_params.get('status')
        key_word = request.query_params.get('key_word')
        api_user = request.user.api_users.get(type='user')

        platform = verify_request(api_user, platform_name, platform_id)


        #TODO check platform in user_subscription
        
        campaigns = platform.campaigns.all()
        if campaign_status == 'history':
            campaigns = campaigns.filter(end_at__lt=datetime.now())
        elif campaign_status == 'schedule':
            campaigns = campaigns.filter(end_at__gte=datetime.now())
        if key_word:
            campaigns = campaigns.filter(title__icontains=str(key_word))
        if order_by:
            campaigns = campaigns.order_by(order_by)

        page = self.paginate_queryset(campaigns)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(campaigns, many=True)
            data = serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create_campaign', parser_classes=(MultiPartParser,IsAuthenticated))
    @action(detail=False, methods=['POST'], url_path=r'create_campaign', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated, PlatfomrIsCampaignOwner,))
    @api_error_handler
    def create_campaign(self, request):
        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')
        api_user = request.user.api_users.get(type='user')

        platform = verify_request(api_user, platform_name, platform_id)
        # TODO check platform in user_subscription
        
        json_data = json.loads(request.data["data"])
        json_data['created_by'] = api_user.id
        json_data['facebook_page'] = platform.id if platform_name == 'facebook' else None

        #TODO
        # json_data['youtube_channel'] = platform.id if platform_name == 'youtube' else None
        json_data['youtube_channel'] = platform.id if platform_name == 'youtube' else 1

        json_data['instagram_profile'] = platform.id if platform_name == 'instagram' or platform_name == 'facebook' else None

        serializer = CampaignSerializerCreate(data=json_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        campaign = serializer.save()

        for key, value in request.data.items():
            if "account" in key:
                account_number = key.split("_")[1]
                image_path = default_storage.save(
                    f'/campaign/{campaign.id}/payment/direct_payment/accounts/{account_number}/{value.name}',
                    ContentFile(value.read()))
                print(f"image_path: {image_path}")
                json_data["meta_payment"]["sg"]["direct_payment"]["accounts"][account_number]["image"] = image_path
        serializer = self.get_serializer(
            campaign, data=json_data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update_campaign', parser_classes=(MultiPartParser,IsAuthenticated))
    @api_error_handler
    def update_campaign(self, request, pk=None):
        # platform_name = request.query_params.get('platform_name')
        # platform_id = request.query_params.get('platform_id')
        # api_user = request.user.api_users.get(type='user')
        # _, campaign = verify_request(
        #     api_user, platform_name, platform_id, campaign_id=pk)
        # yt_access_token = campaign.youtube_campaign.get("access_token", "")
        # yt_refresh_token = campaign.youtube_campaign.get("refresh_token", "")
        # json_data = json.loads(request.data["data"])
        # json_data["youtube_campaign"]["access_token"] = yt_access_token
        # json_data["youtube_campaign"]["refresh_token"] = yt_refresh_token
        # for key, value in request.data.items():
        #     if "account" in key:
        #         account_number = key.split("_")[1]
        #         image_path = default_storage.save(
        #             f'/campaign/{campaign.id}/payment/direct_payment/accounts/{account_number}/{value.name}', ContentFile(value.read()))
        #         print(f"image_path: {image_path}")
        #         json_data["meta_payment"]["sg"]["direct_payment"]["accounts"][account_number]["image"] = image_path
        # serializer = self.get_serializer(
        #     campaign, data=json_data, partial=True)
        # if not serializer.is_valid():
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # serializer.save()

        # return Response(serializer.data, status=status.HTTP_200_OK)

        api_user, platform_name, platform_id = getparams(request, ("platform_name", "platform_id"), with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        campaign = Verify.get_campaign_from_platform(platform, pk)

        #temp solution : no to overide campaign data
        json_data = json.loads(request.data["data"])
        facebook_campaign = campaign.facebook_campaign.__dict__
        facebook_campaign.update(json_data.get("facebook_campaign",{}))
        json_data['facebook_campaign']=facebook_campaign

        youtube_campaign = campaign.youtube_campaign.__dict__
        youtube_campaign.update(json_data.get("youtube_campaign",{}))
        json_data['youtube_campaign']=youtube_campaign

        instagram_campaign = campaign.instagram_campaign.__dict__
        instagram_campaign.update(json_data.get("instagram_campaign",{}))
        json_data['instagram_campaign']=instagram_campaign


        for key, value in request.data.items():
            if "account" in key:
                account_number = key.split("_")[1]
                image_path = default_storage.save(
                    f'/campaign/{campaign.id}/payment/direct_payment/accounts/{account_number}/{value.name}', ContentFile(value.read()))
                print(f"image_path: {image_path}")
                json_data["meta_payment"]["sg"]["direct_payment"]["accounts"][account_number]["image"] = image_path

        serializer = CampaignSerializer(
            campaign, data=json_data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)



    @action(detail=True, methods=['DELETE'], url_path=r'delete_campaign', permission_classes = (IsAuthenticated,))
    @api_error_handler
    def delete_campaign(self, request, pk=None):
        platform_name = request.query_params.get('platform_name')
        platform_id = request.query_params.get('platform_id')
        api_user = request.user.api_users.get(type='user')

        _, campaign = verify_request(
            api_user, platform_name, platform_id, campaign_id=pk)
        campaign.delete()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'ig_comment', permission_classes = (IsAuthenticated,))
    @api_error_handler
    def seller_total_revenue(self, request):
        api_user = request.user.api_users.get(type='user')
        campaign_id = request.query_params.get('campaign_id')
        comment_id = request.query_params.get('comment_id')
        platform = request.query_params.get('platform')
        comments_list = []

        is_user = verify_seller_request(api_user)
        if is_user:
            if int(comment_id) == 0:
                comment_datas = db.api_campaign_comment.find({'campaign_id': int(campaign_id), 'platform': 'instagram'})
                for comment_data in comment_datas:
                    commentJson = {}
                    commentJson['customer_name'] = comment_data['customer_name']
                    commentJson['id'] = comment_data['id']                        
                    commentJson['message'] = comment_data['message']
                    commentJson['created_at'] = comment_data['created_time']
                    commentJson['image'] = comment_data['image']
                    comments_list.append(commentJson)
            else:
                last_time = db.api_campaign_comment.find_one({'campaign_id': int(campaign_id), 'id': comment_id, 'platform': 'instagram'})['created_time']
                comment_datas = db.api_campaign_comment.find({'campaign_id': int(campaign_id), 'created_time': {'$gt': last_time}, 'platform': 'instagram'})
                for comment_data in comment_datas:
                    commentJson = {}
                    commentJson['customer_name'] = comment_data['customer_name']
                    commentJson['id'] = comment_data['id']                        
                    commentJson['message'] = comment_data['message']
                    commentJson['created_at'] = comment_data['created_time']
                    commentJson['image'] = comment_data['image']
                    comments_list.append(commentJson)

        return Response(comments_list, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'bind_youtube_channel' ,permission_classes=(IsAuthenticated,))
    @api_error_handler
    def bind_youtube_channel(self, request):

        api_user, platform_name, platform_id, youtube_channel_id, google_access_token, campaign_id = getparams(request, ("platform_name", "platform_id", "youtube_channel_id", "campaign_id"), with_user=True, seller=True)
        
        platform = Verify.get_platform(api_user, platform_name, platform_id)

        user_subscription = Verify.get_user_subscription_from_platform(platform)
        

        if not YoutubeChannel.objects.filter(channel_id = youtube_channel_id).exists():
            raise ApiVerifyError('youtube channel not exists')

        youtube_channel = YoutubeChannel.objects.get(channel_id = youtube_channel_id)
        campaign = Verify.get_campaign_from_platform(platform, campaign_id)

        user_subscription.youtube_channel.add(youtube_channel)

        pass 