import json

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from api.models.campaign.campaign import Campaign, CampaignSerializer, CampaignSerializerEdit, CampaignSerializerRetreive, CampaignSerializerCreate
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime

from backend.pymongo.mongodb import db
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from api.utils.common.common import getparams
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from bson.json_util import loads, dumps


def verify_seller_request(api_user):
    Verify.verify_user(api_user)
    return True


class CampaignPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


class CampaignViewSet(viewsets.ModelViewSet):
    
    queryset = Campaign.objects.all().order_by('id')
    serializer_class = CampaignSerializer
    filterset_fields = []
    pagination_class = CampaignPagination

    @action(detail=True, methods=['GET'], url_path=r'retrieve_campaign', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def retrieve_campaign(self, request, pk=None):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaign = Verify.get_campaign_from_user_subscription(user_subscription,pk)

        return Response(CampaignSerializerRetreive(campaign).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'retrieve_campaign_buyer')
    @api_error_handler
    def retrieve_campaign_buyer(self, request, pk=None):
        campaign_data = db.api_campaign.find_one({'id': int(pk)})
        campaign_data.pop('_id', None)
        # serializer = Campaign.objects.get(id=pk)

        return Response(campaign_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list_campaign', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_campaign(self, request):
        api_user, key_word, campaign_status, order_by = getparams(request,("key_word", "status", "order_by"), with_user=True, seller=True)
        
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaigns = user_subscription.campaigns.filter(id__isnull=False) # Due to problematic dirty data
        if campaign_status == 'history':
            campaigns = campaigns.filter(end_at__lt=datetime.utcnow())
        elif campaign_status == 'schedule':
            campaigns = campaigns.filter(end_at__gte=datetime.utcnow())
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

    #for lss v2
    @action(detail=False, methods=['GET'], url_path=r'search_list', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def search_campaign(self, request):

        api_user, keyword, search_column = getparams(request,("keyword", "search_column"), with_user=True, seller=True)
        
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        queryset = user_subscription.campaigns.filter(id__isnull=False).order_by('-id') # Due to problematic dirty data

        if search_column and keyword and search_column!='undefined' and keyword != 'undefined': 
            if search_column=='id':
                kwargs = { search_column : keyword }
            else:
                kwargs = { search_column + '__icontains': keyword }
            queryset = queryset.filter(**kwargs)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CampaignSerializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = CampaignSerializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create_campaign', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @api_error_handler
    def create_campaign(self, request):
        # platform_name = request.query_params.get('platform_name')
        # platform_id = request.query_params.get('platform_id')

        api_user = Verify.get_seller_user(request)
        # platform = verify_request(api_user, platform_name, platform_id)

        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        # campaigns = user_subscription.campaigns.all()
        
        json_data = json.loads(request.data["data"])
        json_data['created_by'] = api_user.id
        json_data['user_subscription'] = user_subscription.id
        print(json_data)
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

    @action(detail=True, methods=['PUT'], url_path=r'update_campaign', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_campaign(self, request, pk=None):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaign = Verify.get_campaign_from_user_subscription(user_subscription, pk)


        #temp solution : no to overide campaign data
        json_data = json.loads(request.data["data"])
        
        facebook_campaign = campaign.facebook_campaign.copy()
        facebook_campaign.update(json_data.get("facebook_campaign",{}))
        json_data['facebook_campaign']=facebook_campaign

        youtube_campaign = campaign.youtube_campaign.copy()
        youtube_campaign.update(json_data.get("youtube_campaign",{}))
        json_data['youtube_campaign']=youtube_campaign

        instagram_campaign = campaign.instagram_campaign.copy()
        instagram_campaign.update(json_data.get("instagram_campaign",{}))
        json_data['instagram_campaign']=instagram_campaign

        for key, value in request.data.items():
            if "account" in key:
                account_number = key.split("_")[1]
                image_path = default_storage.save(
                    f'/campaign/{campaign.id}/payment/direct_payment/accounts/{account_number}/{value.name}', ContentFile(value.read()))
                print(f"image_path: {image_path}")
                json_data["meta_payment"]["sg"]["direct_payment"]["accounts"][account_number]["image"] = image_path

        serializer = CampaignSerializerEdit(
            campaign, data=json_data, partial=True)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete_campaign', permission_classes = (IsAuthenticated, ))
    @api_error_handler
    def delete_campaign(self, request, pk=None):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaign = Verify.get_campaign_from_user_subscription(user_subscription)

        campaign.user_subscription = None
        campaign.facebook_page = None
        campaign.youtube_page = None
        campaign.instagram_profile = None
        campaign.save()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'bind_facebook_page', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def bind_facebook_page_to_campaign(self, request, pk=None):

        api_user, facebook_page_id = getparams(request, ('facebook_page_id',),with_user=True, seller=True)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaign = Verify.get_campaign_from_user_subscription(user_subscription, pk)

        if 'facebook' not in user_subscription.user_plan.get('activated_platform'):
           raise ApiVerifyError('facebook not activated')

        facebook_page = Verify.get_facebook_page_from_user_subscription(user_subscription, facebook_page_id)
        campaign.facebook_page = facebook_page
        campaign.save()
        return Response(CampaignSerializerRetreive(campaign).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'bind_youtube_channel', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def bind_youtube_channel_to_campaign(self, request, pk=None):

        api_user, youtube_channel_id = getparams(request, ('youtube_channel_id',),with_user=True, seller=True)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaign = Verify.get_campaign_from_user_subscription(user_subscription, pk)

        if 'youtube' not in user_subscription.user_plan.get('activated_platform'):
           raise ApiVerifyError('youtube not activated')

        youtube_channel = Verify.get_youtube_channel_from_user_subscription(user_subscription, youtube_channel_id)
        campaign.youtube_channel = youtube_channel
        campaign.save()
        return Response(CampaignSerializerRetreive(campaign).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'bind_instagram_profile', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def bind_instagram_profile_to_campaign(self, request, pk=None):

        api_user, instagram_profile_id = getparams(request, ('instagram_profile_id',),with_user=True, seller=True)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaign = Verify.get_campaign_from_user_subscription(user_subscription, pk)

        if 'instagram' not in user_subscription.user_plan.get('activated_platform'):
           raise ApiVerifyError('instagram not activated')

        instagram_profile = Verify.get_instagram_profile_from_user_subscription(user_subscription, instagram_profile_id)
        campaign.instagram_profile = instagram_profile
        campaign.save()
        return Response(CampaignSerializerRetreive(campaign).data, status=status.HTTP_200_OK)


    #TODO @Dereck Move to instagram_profile view
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
                comments_list = self.__create_comments_list(comment_datas)
            else:
                last_time = db.api_campaign_comment.find_one({'campaign_id': int(campaign_id), 'id': comment_id, 'platform': 'instagram'})['created_time']
                comment_datas = db.api_campaign_comment.find({'campaign_id': int(campaign_id), 'created_time': {'$gt': last_time}, 'platform': 'instagram'})
                comments_list = self.__create_comments_list(comment_datas)

        return Response(comments_list, status=status.HTTP_200_OK)



    @action(detail=True, methods=['GET'], url_path=r'comments/summarize', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def comment_category_summarize(self, request, pk):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        Verify.get_campaign_from_user_subscription(user_subscription, pk)

        ret = []
        categories = ['neutro', 'delivery', 'payment']
        total_comment_count = db.api_campaign_comment.find({"campaign_id":int(pk)}).count()
        
        for category in categories:
            comment_count = db.api_campaign_comment.find({"campaign_id":int(pk),"categories":{"$elemMatch":{'$eq':category}}}).count()
            ret.append({"name":category,"comment_count":comment_count,"total_comment_count":total_comment_count})
        
        return Response(ret, status=status.HTTP_200_OK)


    @action(detail=True, methods=['GET'], url_path=r'comments/category/(?P<category_name>[^/.]+)/list', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def comment_category_list(self, request, pk, category_name):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        Verify.get_campaign_from_user_subscription(user_subscription, pk)

        comments = db.api_campaign_comment.find({"campaign_id":int(pk),"categories":{"$elemMatch":{'$eq':category_name}}},{"_id":0})
        comments_str = dumps(comments)
        comments_json = loads(comments_str)
        
        return Response(comments_json, status=status.HTTP_200_OK)

    def __create_comments_list(self, comment_datas) -> list:
        comments_list = []
        for comment_data in comment_datas:
            comment_json = {'customer_name': comment_data['customer_name'], 'id': comment_data['id'],
                            'message': comment_data['message'], 'created_at': comment_data['created_time'],
                            'image': comment_data['image']}
            comments_list.append(comment_json)

        return comments_list