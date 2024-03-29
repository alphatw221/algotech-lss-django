from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.conf import settings

from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action

from datetime import datetime
from api import models
from api_v2 import rule
import api
import database
import lib
import json
import service

    
class CampaignPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = models.campaign.campaign.Campaign.objects.all().order_by('id')
    serializer_class = models.campaign.campaign.CampaignSerializer
    pagination_class = CampaignPagination
    permission_classes = (IsAdminUser,)


    #--------------------------------------------- buyer ---------------------------------------------------------
    @action(detail=True, methods=['GET'], url_path=r'buyer/retrieve', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_campaign(self, request, pk):
        campaign = lib.util.verify.Verify.get_campaign((pk))
        return Response(models.campaign.campaign.CampaignSerializer(campaign).data, status=status.HTTP_200_OK)


    #--------------------------------------------- seller ---------------------------------------------------------
    @action(detail=False, methods=['GET'], url_path=r'list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_campaign(self, request):

        api_user, keyword, campaign_status, order_by, search_column = \
            lib.util.getter.getparams(request,("keyword", "status", "order_by","searchColumn"), with_user=True, seller=True)
        
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaigns = user_subscription.campaigns.filter(id__isnull=False) # Due to problematic dirty data
        if campaign_status == 'history':
            campaigns = campaigns.filter(end_at__lt=datetime.utcnow())
        elif campaign_status == 'scheduled':
            campaigns = campaigns.filter(start_at__gte=datetime.utcnow(), end_at__gte=datetime.utcnow())
        elif campaign_status == 'ongoing':
            campaigns = campaigns.filter(start_at__lte=datetime.utcnow(), end_at__gte=datetime.utcnow())
        if order_by:
            campaigns = campaigns.order_by("-"+order_by)
        
        kwargs = {}
        if (search_column in ["", None]) and (keyword not in [None, ""]):
            raise lib.error_handle.error.api_error.ApiVerifyError("search_can_not_empty")
        if (search_column not in ['undefined', '']) and (keyword not in ['undefined', '', None]):
            kwargs = { search_column + '__icontains': keyword }

        campaigns = campaigns.filter(**kwargs)
        page = self.paginate_queryset(campaigns)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(campaigns, many=True)
            data = serializer.data
        
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list/(?P<_status>[^/.]+)/options', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_campaign_option(self, request, _status):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaigns = user_subscription.campaigns.filter(id__isnull=False) # Due to problematic dirty data
        if _status == models.campaign.campaign.STATUS_HISTORY:
            campaigns = campaigns.filter(end_at__lt=datetime.utcnow())
        elif _status == models.campaign.campaign.STATUS_SCHEDULED:
            campaigns = campaigns.filter(end_at__gte=datetime.utcnow())
        elif _status == models.campaign.campaign.STATUS_ONGOING:
            campaigns = campaigns.filter(end_at__gte=datetime.utcnow())
            campaigns = campaigns.filter(start_at__lte=datetime.utcnow())
        else:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid status')
        return Response(models.campaign.campaign.CampaignOptionSerializer(campaigns, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create', parser_classes=(MultiPartParser, ), permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def create_campaign(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        campaignData, = lib.util.getter.getdata(request, ('data',), required=True)
        campaignData = json.loads(campaignData)
        
            
        end_at = campaignData['end_at']
        supplier_id = campaignData.get("supplier")
        if supplier_id not in ["", None, "null", "undefined"]:
            supplier = lib.util.verify.Verify.get_support_stock_user_subscriptions_from_user_subscription(supplier_id,user_subscription)
            campaignData.update({
                "meta_logistic": supplier.meta_logistic,
            })
        # kol will use dealer's payment
        if user_subscription.type == "kol":
            dear_subscription = user_subscription.dealer
            if not dear_subscription:
                raise lib.error_handle.error.api_error.ApiVerifyError('not_belong_to_any_dealer')
            campaignData.update({
                "meta_payment": dear_subscription.meta_payment
            })
        ret = rule.rule_checker.user_subscription_rule_checker.CreateCampaignRuleChecker.check(**{
            'api_user': api_user, 'user_subscription': user_subscription, 'end_at': end_at
        })
        
        

        serializer = models.campaign.campaign.CampaignSerializerCreate(data=campaignData)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        campaign = serializer.save()
        campaign.created_by = api_user
        campaign.user_subscription = user_subscription



        if accounts:=campaign.meta_payment.get('direct_payment',{}).get('v2_accounts'):
            for index, account in enumerate(accounts):
                key = account.get('name','')+f'_{index}'
                image=request.data.get(key)
                if image in ['null', None, '', 'undefined']:
                    continue
                elif image =='._no_image':
                    account['image'] = settings.GOOGLE_STORAGE_STATIC_DIR+models.campaign.campaign.IMAGE_NULL
                    continue
                elif image.size > models.campaign.campaign.IMAGE_MAXIMUM_SIZE:
                    continue
                elif image.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
                    continue
                
                account_name = account.get('name','')
                image_name = image.name.replace(" ","")
                image_dir = f'campaign/{campaign.id}/payment/direct_payment/accounts/{account_name}'
                image_url = lib.util.storage.upload_image(image_dir, image_name, image)
                account['image'] = image_url

        campaign.save()
        
        return Response(models.campaign.campaign.CampaignSerializer(campaign).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update', parser_classes=(MultiPartParser, ), permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_campaign(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)

        campaign_data, = lib.util.getter.getdata(request, ('data',), required=True)
        campaign_data = json.loads(campaign_data)
        supplier_id = ''
        if campaign_data.get("supplier", {}):
            supplier_id = campaign_data.get("supplier", {}).get('id', '')
        if supplier_id not in ["", "null", "undefined"]:
            supplier = lib.util.verify.Verify.get_support_stock_user_subscriptions_from_user_subscription(supplier_id,user_subscription)
            campaign_data.update({
                "meta_logistic": supplier.meta_logistic,
            })
        # kol will use dealer's payment
        if user_subscription.type == "kol":
            dear_subscription = user_subscription.dealer
            if not dear_subscription:
                raise lib.error_handle.error.api_error.ApiVerifyError('not_belong_to_any_dealer')
            campaign_data.update({
                "meta_payment": dear_subscription.meta_payment
            })
        ret = rule.rule_checker.user_subscription_rule_checker.RuleChecker.check(
            check_list=[
                rule.check_rule.user_subscription_check_rule.UserSubscriptionCheckRule.is_expired,
                rule.check_rule.user_subscription_check_rule.UserSubscriptionCheckRule.campaign_end_time_over_subscription_period,
                rule.check_rule.user_subscription_check_rule.UserSubscriptionCheckRule.max_concurrent_live,
                rule.check_rule.user_subscription_check_rule.UserSubscriptionCheckRule.campaign_limit,
            ],**{
                'api_user': api_user, 'user_subscription': user_subscription, 'campaign_data': campaign_data
            })

        serializer = models.campaign.campaign.CampaignSerializerUpdate(campaign, data=campaign_data, partial=True)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        campaign = serializer.save()

        save = False
        if accounts:=campaign.meta_payment.get('direct_payment',{}).get('v2_accounts'):
            for index, account in enumerate(accounts):
                key = account.get('name','')+f'_{index}'
                image=request.data.get(key)
                if image in ['null', None, '', 'undefined']:
                    continue
                elif image == '._no_image':
                    account['image'] = settings.GOOGLE_STORAGE_STATIC_DIR+models.campaign.campaign.IMAGE_NULL
                    save=True
                    continue
                elif image.size > models.campaign.campaign.IMAGE_MAXIMUM_SIZE:
                    continue
                elif image.content_type not in models.campaign.campaign.IMAGE_SUPPORTED_TYPE:
                    continue
                
                account_name = account.get('name','')
                image_name = image.name.replace(" ","")
                image_dir = f'campaign/{campaign.id}/payment/direct_payment/accounts/{account_name}'
                image_url = lib.util.storage.upload_image(image_dir, image_name, image)
                account['image'] = image_url
                
                save=True

        if save:
            campaign.save()
        
        return Response(models.campaign.campaign.CampaignSerializer(campaign).data, status=status.HTTP_200_OK)

    
    
    @action(detail=True, methods=['GET'], url_path=r'retrieve', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_campaign(self, request, pk):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)

        return Response(models.campaign.campaign.CampaignSerializer(campaign).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['DELETE'], url_path=r'delete', permission_classes = (IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_campaign(self, request, pk):


        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription,pk)

        campaign.user_subscription = None
        campaign.end_at = datetime.utcnow()
        campaign.save()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'check_facebook_page_token', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_facebook_page_token(self, request):

        api_user, facebook_page_id = lib.util.getter.getparams(request, ('facebook_page_id',),with_user=True, seller=True)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if 'facebook' not in user_subscription.user_plan.get('activated_platform'):
           raise lib.error_handle.error.api_error.ApiVerifyError('facebook_not_activated')
        
        facebook_page = lib.util.verify.Verify.get_facebook_page_from_user_subscription(user_subscription, facebook_page_id)
        is_token_valid = lib.util.verify.Verify.check_is_page_token_valid('facebook', facebook_page.token, facebook_page.page_id)
        if not is_token_valid:
            raise lib.error_handle.error.api_error.ApiVerifyError(f"Facebook page <{facebook_page.name}>: token expired or invalid. Please re-bind your page on Platform page.")
        return Response(models.facebook.facebook_page.FacebookPageSerializer(facebook_page).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'check_youtube_channel_token', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_youtube_channel_token(self, request):

        api_user, youtube_channel_id = lib.util.getter.getparams(request, ('youtube_channel_id',),with_user=True, seller=True)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        if 'youtube' not in user_subscription.user_plan.get('activated_platform'):
           raise lib.error_handle.error.api_error.ApiVerifyError('youtube not activated')

        youtube_channel = lib.util.verify.Verify.get_youtube_channel_from_user_subscription(user_subscription, youtube_channel_id)
        print(youtube_channel)
        
        response_status, response = service.google.user.api_google_post_refresh_token(youtube_channel.refresh_token)
        print(response)
        is_token_valid = lib.util.verify.Verify.check_is_page_token_valid('youtube', response['access_token'])
        if not is_token_valid:
            raise lib.error_handle.error.api_error.ApiVerifyError(f"YouTube channel <{youtube_channel.name}>: token expired or invalid. Please re-bind your channel on Platform page.")
        youtube_channel.token = response['access_token']
        youtube_channel.save()
        return Response(models.youtube.youtube_channel.YoutubeChannelSerializer(youtube_channel).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'check_instagram_profile_token', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_instagram_profile_token(self, request):

        api_user, instagram_profile_id = lib.util.getter.getparams(request, ('instagram_profile_id',),with_user=True, seller=True)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        if 'instagram' not in user_subscription.user_plan.get('activated_platform'):
           raise lib.error_handle.error.api_error.ApiVerifyError('instagram not activated')

        instagram_profile = lib.util.verify.Verify.get_instagram_profile_from_user_subscription(user_subscription, instagram_profile_id)
        is_token_valid = lib.util.verify.Verify.check_is_page_token_valid('instagram', instagram_profile.token, instagram_profile.business_id)
        if not is_token_valid:
            raise lib.error_handle.error.api_error.ApiVerifyError(f"Instagram profile <{instagram_profile.name}>: token expired or invalid. Please re-bind your profile on Platform page.")
        return Response(models.instagram.instagram_profile.InstagramProfileSerializer(instagram_profile).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['PUT'], url_path=r'save_pages_info', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def save_pages_info(self, request, pk):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)
        
        data = request.data
        print(data)
        if post_id := data.get("facebook", {}).get("post_id", {}):
            facebook_page = lib.util.verify.Verify.get_facebook_page_from_user_subscription(user_subscription, data.get("facebook", {}).get("page_id", {}), field="page_id")
            campaign.facebook_page = facebook_page
            campaign.facebook_campaign['post_id'] = post_id
        if live_video_id := data.get("youtube", {}).get("live_video_id", {}):
            youtube_channel = lib.util.verify.Verify.get_youtube_channel_from_user_subscription(user_subscription, data.get("youtube", {}).get("channel_id", {}), field="channel_id")
            campaign.youtube_channel = youtube_channel
            campaign.youtube_campaign['live_video_id'] = live_video_id
        if live_media_id := data.get("instagram", {}).get("live_media_id", {}):
            instagram_profile = lib.util.verify.Verify.get_instagram_profile_from_user_subscription(user_subscription, data.get("instagram", {}).get("profile_id", {}), field="business_id")
            campaign.instagram_profile = instagram_profile
            campaign.instagram_campaign['live_media_id'] = live_media_id
        campaign.save()
        
        return Response("ok", status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'live/update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_campaign_live_data(self, request, pk):
        platform, platform_id, post_id, username = \
            lib.util.getter.getdata(request, ("platform", "platform_id", "post_id", "username"), required=False)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = \
            lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)

        if platform not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiCallerError(f'{platform} not activated')

        if platform=='facebook':
            facebook_page = lib.util.verify.Verify.get_facebook_page_from_user_subscription(user_subscription, platform_id)
            campaign.facebook_campaign['post_id']=post_id
            campaign.facebook_page = facebook_page
        elif platform=='sub_facebook':
            facebook_page = lib.util.verify.Verify.get_facebook_page_from_user_subscription(user_subscription, platform_id)
            campaign.sub_facebook_campaign['post_id']=post_id
            campaign.sub_facebook_page = facebook_page
        elif platform=='sub_facebook_3':
            facebook_page = lib.util.verify.Verify.get_facebook_page_from_user_subscription(user_subscription, platform_id)
            campaign.sub_facebook_campaign_3['post_id']=post_id
            campaign.sub_facebook_page_3 = facebook_page
        elif platform=='sub_facebook_4':
            facebook_page = lib.util.verify.Verify.get_facebook_page_from_user_subscription(user_subscription, platform_id)
            campaign.sub_facebook_campaign_4['post_id']=post_id
            campaign.sub_facebook_page_4 = facebook_page
        elif platform=='sub_facebook_5':
            facebook_page = lib.util.verify.Verify.get_facebook_page_from_user_subscription(user_subscription, platform_id)
            campaign.sub_facebook_campaign_5['post_id']=post_id
            campaign.sub_facebook_page_5 = facebook_page
        elif platform=='sub_facebook_6':
            facebook_page = lib.util.verify.Verify.get_facebook_page_from_user_subscription(user_subscription, platform_id)
            campaign.sub_facebook_campaign_6['post_id']=post_id
            campaign.sub_facebook_page_6 = facebook_page

        elif platform =='youtube':
            youtube_channel = lib.util.verify.Verify.get_youtube_channel_from_user_subscription(user_subscription, platform_id)
            campaign.youtube_campaign['live_video_id']=post_id
            campaign.youtube_channel = youtube_channel
        elif platform =='instagram':
            instagram_profile = lib.util.verify.Verify.get_instagram_profile_from_user_subscription(user_subscription, platform_id)
            campaign.instagram_campaign['live_media_id']=post_id
            campaign.instagram_profile = instagram_profile
        elif platform == 'twitch':
            twitch_channel = lib.util.verify.Verify.get_twitch_channel_from_user_subscription(user_subscription, platform_id)
            campaign.twitch_campaign['channel_name'] = twitch_channel.name
            campaign.twitch_campaign['token']=twitch_channel.token
            campaign.twitch_campaign['user_name']=twitch_channel.user_name
            campaign.twitch_channel = twitch_channel
        elif platform == 'tiktok':
            # tiktok_account = lib.util.verify.Verify.get_tiktok_channel_from_user_subscription(user_subscription, platform_id)
            campaign.tiktok_campaign['username'] = username
            # campaign.tiktok_account = tiktok_account
        campaign.save()
        # return Response(models.campaign.campaign.CampaignSerializerRetreive(campaign).data, status=status.HTTP_200_OK)
        return Response(models.campaign.campaign.CampaignSerializer(campaign).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'live/delete/(?P<platform>[^/.]+)', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_campaign_live_data(self, request, pk,platform):
        # platform = \
        #     lib.util.getter.getdata(request, ("platform",), required=False)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = \
            lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)

        if platform not in user_subscription.user_plan.get('activated_platform'):
            raise lib.error_handle.error.api_error.ApiCallerError(f'{platform} not activated')

        if platform=='facebook':
            campaign.facebook_campaign['post_id']=''
            campaign.facebook_page = None
        elif platform=='sub_facebook':
            campaign.sub_facebook_campaign['post_id']=''
            campaign.sub_facebook_page = None
        elif platform=='sub_facebook_3':
            campaign.sub_facebook_campaign_3['post_id']=''
            campaign.sub_facebook_page_3 = None
        elif platform=='sub_facebook_4':
            campaign.sub_facebook_campaign_4['post_id']=''
            campaign.sub_facebook_page_4 = None
        elif platform=='sub_facebook_5':
            campaign.sub_facebook_campaign_5['post_id']=''
            campaign.sub_facebook_page_5 = None
        elif platform=='sub_facebook_6':
            campaign.sub_facebook_campaign_6['post_id']=''
            campaign.sub_facebook_page_6 = None
        elif platform =='youtube':
            campaign.youtube_campaign['live_video_id']=''
            campaign.youtube_channel = None
        elif platform =='instagram':
            campaign.instagram_campaign['live_media_id']=''
            campaign.instagram_profile = None
        elif platform == 'twitch':
            campaign.twitch_campaign['channel_name'] = ''
            campaign.twitch_campaign['token']=''
            campaign.twitch_campaign['user_name']=''
            campaign.twitch_channel = None
        elif platform == 'tiktok':
            # tiktok_account = lib.util.verify.Verify.get_tiktok_channel_from_user_subscription(user_subscription, platform_id)
            campaign.tiktok_campaign['username'] = ''
            # campaign.tiktok_account = tiktok_account
        campaign.save()
        # return Response(models.campaign.campaign.CampaignSerializerRetreive(campaign).data, status=status.HTTP_200_OK)
        return Response(models.campaign.campaign.CampaignSerializer(campaign).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'delivery/setting/update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def save_delivery_default_settings(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        delivery_setting = request.data
        delivery_setting = delivery_setting.get('_value', {})

        user_subscription.meta_logistic = delivery_setting
        user_subscription.save()

        return Response("success", status=status.HTTP_200_OK) 
    

    @action(detail=False, methods=['GET'], url_path=r'delivery/setting/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_delivery_default_settings(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        data = user_subscription.meta_logistic
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'facebook/comment-on-comment', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def facebook_post_comment(self, request):
        api_user, campaign_id, comment_id, message = \
            lib.util.getter.getparams(request, ("campaign_id","comment_id", "message"), with_user=True, seller=True)
        
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
        page_token = campaign.facebook_page.token

        data = service.facebook.post.post_page_comment_on_comment(page_token,comment_id,message)
        

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'facebook/comment-reply', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def facebook_get_comment_reply(self, request):
        api_user, campaign_id, comment_id = \
            lib.util.getter.getparams(request, ("campaign_id","comment_id"), with_user=True, seller=True)
        
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
        page_token = campaign.facebook_page.token
        data = service.facebook.page.get_comments_on_comment(page_token,comment_id)
        

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'stop_checkout/toggle', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def toggle_stop_checkout_status(self, request):

        api_user, campaign_id= lib.util.getter.getparams(request, ('campaign_id', ))

        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription,campaign_id)

        campaign.stop_checkout = not campaign.stop_checkout   
        campaign.save()

        return Response(models.campaign.campaign.CampaignSerializer(campaign).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['POST'], url_path=r'product/add/fast', permission_classes=(IsAuthenticated,) )
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def fast_add_product(self, request, pk):

        save_to_stock, name, order_code, price, qty = lib.util.getter.getdata(request,("save_to_stock", "name", "order_code", "price", "qty"), required=True)
        
        category_id, = lib.util.getter.getdata(request,("category_id",), required=False)
        
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)
        
        if category_id and user_subscription.product_categories.filter(id=int(category_id)).exists():
            category = [category_id]
        else:
            category = []

        product=None
        
        if campaign.products.filter(order_code=order_code).exists():
            raise lib.error_handle.error.api_error.ApiVerifyError('duplicate_order_code')

        if save_to_stock:
            product = models.product.product.Product.objects.create(user_subscription=user_subscription, created_by=api_user, name=name, order_code=order_code, categories=category, price=price, qty=0, type=models.product.product.TYPE_PRODUCT, image=settings.GOOGLE_STORAGE_STATIC_DIR+models.product.product.IMAGE_NULL)

        campaign_product = models.campaign.campaign_product.CampaignProduct.objects.create(campaign=campaign, created_by=api_user, product=product, status=True, categories=category, type=models.product.product.TYPE_PRODUCT, name=name, order_code=order_code, price=float(price), qty_for_sale=int(qty), image=settings.GOOGLE_STORAGE_STATIC_DIR+models.campaign.campaign_product.IMAGE_NULL, **user_subscription.meta.get('campaign_product_default_fields',{}))

        return Response(models.campaign.campaign_product.CampaignProductSerializer(campaign_product).data, status=status.HTTP_200_OK)

    
    # @action(detail=True, methods=['GET'], url_path=r'report', permission_classes=(IsAuthenticated, ))
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def generate_campaign_order_report(self, request, pk):

    #     api_user = lib.util.verify.Verify.get_seller_user(request)
    #     user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
    #     campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)
    #     campaign_title = campaign.title.replace(' ','')
    #     buffer = lib.helper.xlsx_helper.OrderReport.create(campaign, user_subscription.lang)

    #     response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    #     response['Content-Disposition'] = f'attachment; filename={campaign_title}.xlsx'
    #     return response
    
    @action(detail=True, methods=['GET'], url_path=r'product/order_code/dict', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_campaign_product_dict(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)

        return Response({str(product.order_code).lower():True for product in campaign.products.all()}, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['GET'], url_path=r'statistics', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_campaign_statistics(self, request, pk):
        """calculate key indicators of a campaign

        Args:
            request object: http request data
            pk str: primary key

        Returns:
            object: response data
        """
        
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)

        previous_campaign_data = database.lss.campaign.get_previous_campaign_data(campaign.id, user_subscription.id)
        previous_campaign_id = previous_campaign_data.get('id', None)

        campaign_cart_count = database.lss.cart.get_count_in_campaign(campaign.id)
        campaign_order_complete_count,campaign_order_proceed_count = database.lss.campaign.get_order_complete_proceed_count(campaign.id) 
        campaign_comment_count = database.lss.campaign_comment.get_count_in_campaign(campaign.id)
        campaign_complete_sales = database.lss.order.get_complete_sales_of_campaign(campaign.id)
        campaign_proceed_sales = database.lss.order.get_proceed_sales_of_campaign(campaign.id)
    
        previous_campaign_cart_count = database.lss.cart.get_count_in_campaign(previous_campaign_id)
        previous_campaign_order_complete_count, perivious_campaign_order_proceed_count = database.lss.campaign.get_order_complete_proceed_count(previous_campaign_id) 
        previous_campaign_comment_count = database.lss.campaign_comment.get_count_in_campaign(previous_campaign_id)
        previous_campaign_complete_sales = database.lss.order.get_complete_sales_of_campaign(previous_campaign_id)
        previous_campaign_proceed_sales = database.lss.order.get_proceed_sales_of_campaign(previous_campaign_id)

        statistics_data = {
            "cart_count":campaign_cart_count,
            "order_complete_count":campaign_order_complete_count,
            "order_proceed_count":campaign_order_proceed_count,
            "comment_count":campaign_comment_count,
            "complete_sales":campaign_complete_sales,
            "proceed_sales": campaign_proceed_sales,

            "previous_cart_count":previous_campaign_cart_count,
            "previous_order_complete_count":previous_campaign_order_complete_count,
            "previous_order_proceed_count":perivious_campaign_order_proceed_count,
            "previous_comment_count":previous_campaign_comment_count,
            "previous_complete_sales":previous_campaign_complete_sales,
            "previous_proceed_sales": previous_campaign_proceed_sales,
        }
        return Response(statistics_data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['GET'], url_path=r'setup/status', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_campaign_setup_status(self, request, pk):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)
        
        ig_media_url = None
        try:
            status_code, response = service.instagram.post.get_post_media_url(campaign.instagram_profile.token, campaign.instagram_campaign.get("live_media_id", ""))
            if status_code == 200:
                ig_media_url = response["media_url"]
        except Exception:
            pass
        res = {
            "all": {
                "fully_setup": True
            },
            "facebook": {
                # "comments":CampaignCommentSerializer(fb_comments, many=True).data,
                "fully_setup": True if (campaign.facebook_campaign.get("post_id", None) and campaign.facebook_page) else False,
                "page_id": campaign.facebook_page.page_id if campaign.facebook_page else None,
                "post_id": campaign.facebook_campaign.get("post_id", None),
            },
            "instagram": {
                # "comments":CampaignCommentSerializer(ig_comments, many=True).data,
                "fully_setup": True if (campaign.instagram_campaign.get("live_media_id", None) and campaign.instagram_profile and ig_media_url) else False,
                "media_url": ig_media_url
            },
            "youtube": {
                # "comments":CampaignCommentSerializer(yt_comments, many=True).data,
                "fully_setup": True if (campaign.youtube_campaign.get("live_video_id", None) and campaign.youtube_channel) else False,
                "live_video_id": campaign.youtube_campaign.get("live_video_id", None) 
            },
            
        }
        return Response(res, status=status.HTTP_200_OK) 



    @action(detail=True, methods=['GET'], url_path=r'link/short', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_short_link(self, request, pk):

        type, = lib.util.getter.getparams(request, ('type',), with_user=False)

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)

        if type=='tiktok':
            destination = f"{settings.GCP_API_LOADBALANCER_URL}/buyer/search/{campaign.id}/cart/tiktok"
        elif user_subscription.require_customer_login:
            if user_subscription.domain:
                destination =  f"https://{user_subscription.domain}/buyer/login/create/{campaign.id}"
            else:
                destination = f"{settings.GCP_API_LOADBALANCER_URL}/buyer/login/create/{campaign.id}"
        else:
            if user_subscription.domain:
                destination =  f"https://{user_subscription.domain}/blank/{campaign.id}"
            else:
                destination = f"{settings.SHOPPING_CART_RECAPTCHA_URL}/blank/{campaign.id}"
        
        success, data = service.rebrandly.rebrandly.create_link(destination)   
        if not success:
            raise lib.error_handle.error.api_error.ApiCallerError('error')

        res = {'link': f"https://{data.get('shortUrl')}" }

        return Response(res, status=status.HTTP_200_OK)
    