from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse


from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action

from datetime import datetime
from api import models, rule
import api
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
            campaigns = campaigns.filter(end_at__gte=datetime.utcnow())
        elif campaign_status == 'ongoing':
            campaigns = campaigns.filter(end_at__gte=datetime.utcnow())
            campaigns = campaigns.filter(start_at__lte=datetime.utcnow())
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
                    account['image'] = models.campaign.campaign.IMAGE_NULL
                    continue
                elif image.size > models.campaign.campaign.IMAGE_MAXIMUM_SIZE:
                    continue
                elif image.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
                    continue
                
                account_name = account.get('name','')
                image_path = default_storage.save(f'/campaign/{campaign.id}/payment/direct_payment/accounts/{account_name}/{image.name}', ContentFile(image.read()))
                account['image'] = image_path

        campaign.save()
        
        return Response(models.campaign.campaign.CampaignSerializer(campaign).data, status=status.HTTP_200_OK)

        # title, period, delivery_info, payments = lib.util.getter.getdata(request, ('campaignTitle', 'campaignPeriod', 'deliverySettings', 'paymentSettings'), required=False)
        # campaing_json = { 
        #     'title': json.loads(title), 
        #     'start_at': json.loads(period).get('start', None),
        #     'end_at': json.loads(period).get('end', None),
        # }
        # campaing_json['created_by'] = api_user.id
        # campaing_json['user_subscription'] = user_subscription.id
        
        # serializer = CampaignSerializerCreate(data=campaing_json)
        # if not serializer.is_valid():
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # campaign = serializer.save()

        # meta_logistic = json.loads(delivery_info)
        # meta_payment = {}
        # for name, payment in json.loads(payments).items():
        #     if name == 'direct_payment':
        #         for key, value in payment.items():
        #             if key == 'accounts':
        #                 for account in value:
        #                     del account['previewImage']
        #                     account_number = account.get('number', '')
        #                     account_image, = lib.util.getter.getdata(request, (account_number, ), required=False)
        #                     if account_image:
        #                         image_path = default_storage.save(f'/campaign/{campaign.id}/payment/direct_payment/accounts/{account_number}/{account_image.name}', ContentFile(account_image.read()))
        #                         account['image'] = image_path
                    
        #         meta_payment['direct_payment'] = payment
        #     else:
        #         meta_payment[name] = payment

        # campaing_json['meta_payment'] = meta_payment
        # campaing_json['meta_logistic'] = meta_logistic
        # serializer = self.get_serializer(
        #     campaign, data=campaing_json, partial=True)
        # if not serializer.is_valid():
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # serializer.save()

        # return Response(models.campaign.campaign.CampaignSerializer(campaign).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['PUT'], url_path=r'update', parser_classes=(MultiPartParser, ), permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_campaign(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)

        campaignData, = lib.util.getter.getdata(request, ('data',), required=True)
        campaignData = json.loads(campaignData)

        serializer = models.campaign.campaign.CampaignSerializerUpdate(campaign, data=campaignData, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        campaign = serializer.save()

        save = False
        if accounts:=campaign.meta_payment.get('direct_payment',{}).get('v2_accounts'):
            for index, account in enumerate(accounts):
                key = account.get('name','')+f'_{index}'
                image=request.data.get(key)
                if image in ['null', None, '', 'undefined']:
                    continue
                elif image.size > models.campaign.campaign.IMAGE_MAXIMUM_SIZE:
                    continue
                elif image.content_type not in models.campaign.campaign.IMAGE_SUPPORTED_TYPE:
                    continue
                elif image == '._no_image':
                    account['image'] = models.campaign.campaign.IMAGE_NULL
                    save=True
                    continue
                account_name = account.get('name','')
                image_path = default_storage.save(f'/campaign/{campaign.id}/payment/direct_payment/accounts/{account_name}/{image.name}', ContentFile(image.read()))
                account['image'] = image_path
                save=True

        if save:
            campaign.save()
        
        return Response(models.campaign.campaign.CampaignSerializer(campaign).data, status=status.HTTP_200_OK)

        # api_user = lib.util.verify.Verify.get_seller_user(request)

        
        # user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        # campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)

        # title, period, delivery_info, payments = lib.util.getter.getdata(request, ('campaignTitle', 'campaignPeriod', 'deliverySettings', 'paymentSettings'), required=False)
        # campaing_json = { 
        #     'title': json.loads(title), 
        #     'start_at': json.loads(period).get('start', None),
        #     'end_at': json.loads(period).get('end', None),
        # }
        # campaing_json['created_by'] = api_user.id
        # campaing_json['user_subscription'] = user_subscription.id

        # meta_logistic = json.loads(delivery_info)
        # meta_payment = {}
        # for name, payment in json.loads(payments).items():
        #     if name == 'direct_payment':
        #         for key, value in payment.items():
        #             if key == 'accounts':
        #                 for account in value:
        #                     if 'previewImage' in account:
        #                         del account['previewImage']
        #                     account_number = account.get('number', '')
        #                     account_image, = lib.util.getter.getdata(request, (account_number, ), required=False)
        #                     if account_image:
        #                         image_path = default_storage.save(f'/campaign/{campaign.id}/payment/direct_payment/accounts/{account_number}/{account_image.name}', ContentFile(account_image.read()))
        #                         account['image'] = image_path
                    
        #         meta_payment['direct_payment'] = payment
        #     else:
        #         meta_payment[name] = payment

        # campaing_json['meta_payment'] = meta_payment
        # campaing_json['meta_logistic'] = meta_logistic

        # serializer = models.campaign.campaign.CampaignSerializerUpdate(
        #     campaign, data=campaing_json, partial=True)
        # if not serializer.is_valid():
        #     print(serializer.errors)
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # campaign = serializer.save()

        # return Response(campaign.id, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'retrieve', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_campaign(self, request):
        api_user, campaign_id = lib.util.getter.getparams(request,("campaign_id", ), with_user=True, seller=True)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        return Response(models.campaign.campaign.CampaignSerializer(campaign).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['DELETE'], url_path=r'delete', permission_classes = (IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_campaign(self, request):

        api_user, campaign_id = lib.util.getter.getparams(request,("campaign_id", ), with_user=True, seller=True)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription,campaign_id)

        print(campaign.user_subscription)
        campaign.user_subscription = None
        print(campaign.user_subscription)
        # campaign.facebook_page = None
        # campaign.youtube_page = None
        # campaign.instagram_profile = None
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
    
    @action(detail=False, methods=['GET'], url_path=r'stop_checkout/toggle')
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
        
        category, = lib.util.getter.getdata(request,("category",), required=False)
        if category in ["", "null", None, 'undefined']:
            category = []
        else:
            category = [category]
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)
        
        product=None
        
        if save_to_stock:
            product = models.product.product.Product.objects.create(user_subscription=user_subscription, created_by=api_user, name=name, order_code=order_code, tag=category, price=price, qty=0, type=models.product.product.TYPE_PRODUCT)

        campaign_product = models.campaign.campaign_product.CampaignProduct.objects.create(campaign=campaign, created_by=api_user, product=product, status=True, type=models.product.product.TYPE_PRODUCT, name=name, order_code=order_code, price=float(price), qty_for_sale=int(qty), image=models.campaign.campaign_product.IMAGE_NULL)

        return Response(models.campaign.campaign_product.CampaignProductSerializer(campaign_product).data, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['GET'], url_path=r'report', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def generate_campaign_order_report(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)
        campaign_title = campaign.title.replace(' ','')
        buffer = lib.helper.xlsx_helper.OrderReport.create(campaign, user_subscription.lang)

        response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={campaign_title}.xlsx'
        return response
    
    @action(detail=True, methods=['GET'], url_path=r'product/order_code/dict', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_campaign_product_dict(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pk)

        return Response({str(product.order_code).lower():True for product in campaign.products.all()}, status=status.HTTP_200_OK)