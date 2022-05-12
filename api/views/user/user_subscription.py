from django.http import HttpResponseRedirect
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.code.subscription_code_manager import SubscriptionCodeManager
from api.models.instagram.instagram_profile import InstagramProfile, InstagramProfileSerializer
from api.models.user.user import User,UserSubscriptionSerializerDealerList
from api.models.user.user_subscription import UserSubscription, UserSubscriptionSerializer, UserSubscriptionSerializerForDealerRetrieve, UserSubscriptionSerializerMeta, UserSubscriptionSerializerSimplify, UserSubscriptionSerializerCreate
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from api.models.facebook.facebook_page import FacebookPage, FacebookPageSerializer
from api.models.youtube.youtube_channel import YoutubeChannel, YoutubeChannelSerializer
from datetime import datetime, timedelta
from api.utils.common.common import getdata
from api.utils.error_handle.error.api_error import ApiCallerError
from backend.api.facebook.page import api_fb_get_page_picture, api_fb_get_page_business_profile
from backend.api.facebook.user import api_fb_get_me_accounts

from rest_framework.parsers import MultiPartParser
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from api.utils.common.verify import Verify, getparams
from api.utils.common.verify import ApiVerifyError
from api.utils.advance_query.user_subscription import get_user_subscription_buyer_list

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.common.common import getparams
from backend.api.instagram.profile import api_ig_get_profile_info
from backend.api.youtube.channel import api_youtube_get_list_channel_by_token
import requests, stripe, pytz, business_policy, lib
from django.conf import settings
from api import rule



class UserSubscriptionPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


platform_dict = {'facebook': FacebookPage,
                 'youtube': YoutubeChannel}


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = ()
    queryset = UserSubscription.objects.all().order_by('id')
    serializer_class = UserSubscriptionSerializerSimplify
    filterset_fields = []
    pagination_class = UserSubscriptionPagination

    @action(detail=False, methods=['POST'], url_path=r'admin_create_user_subscription', permission_classes=(IsAdminUser,))
    @api_error_handler
    def create_user_subscription(self, request):
        print(request.data)
        serializer = UserSubscriptionSerializerCreate(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = serializer.save()
        return Response(UserSubscriptionSerializer(user_subscription).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'admin_create_activate_code', permission_classes=(IsAdminUser,))
    @api_error_handler
    def create_activate_code(self, request):
        user_subscription_id, maximum_usage_count, interval = getdata(request, ('user_subscription_id','maximum_usage_count','interval'))
        code = SubscriptionCodeManager.generate(user_subscription_id, maximum_usage_count, interval)
        return Response(code, status=status.HTTP_200_OK)

        
    @action(detail=False, methods=['POST'], url_path=r'execute_activate_code', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def execute_activate_code(self, request):
        code, platform_name, platform_id = getdata(request,('activation_code','plarform_name','plarform_id'))
        subscription_page_data = SubscriptionCodeManager.execute(code, platform_name, platform_id)
        return Response(subscription_page_data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['GET'], url_path=r'admin_add_platform', permission_classes=(IsAdminUser,))
    @api_error_handler
    def add_platform(self, request, pk=None):
        api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)
        platform = Verify.get_platform(api_user, platform_name, platform_id)
        user_subscription = Verify.get_user_subscription(pk)

        if platform_name == 'facebook':
            user_subscription.facebook_pages.add(platform)
        elif platform_name == 'youtube':
            user_subscription.youtube_channels.add(platform)
        elif platform_name == 'instagram':
            raise ApiVerifyError('Not support !!')

        return Response({'message': "add platform success"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'admin_remove_platform', permission_classes=(IsAdminUser,))
    @api_error_handler
    def remove_platform(self, request, pk=None):
        api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)
        platform = Verify.get_platform(api_user, platform_name, platform_id)
        user_subscription = Verify.get_user_subscription(pk)

        if platform_name == 'facebook':
            user_subscription.facebook_pages.remove(platform)
        elif platform_name == 'youtube':
            user_subscription.youtube_channels.remove(platform)
        elif platform_name == 'instagram':
            raise ApiVerifyError('Not support !!')

        return Response({'message': "remove platform success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'get_meta', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_meta(self, request):
        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        serializer = UserSubscriptionSerializerMeta(user_subscription)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET', 'POST'], url_path=r'hitpay', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_hitpay(self, request):
        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        if request.method == "GET":
            payment_data = user_subscription.meta_payment.get("hitpay", {})
            
            return Response(payment_data, status=status.HTTP_200_OK)
        else:
            meta_payment = user_subscription.meta_payment.copy()
            meta_payment['hitpay'] = request.data

            serializer = UserSubscriptionSerializerMeta(
                user_subscription, data={"meta_payment": meta_payment}, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET', 'POST'], url_path=r'paypal', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_paypal(self, request):
        # api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        if request.method == "GET":
            payment_data = user_subscription.meta_payment.get("paypal", {})
            
            return Response(payment_data, status=status.HTTP_200_OK)
        else:
            meta_payment = user_subscription.meta_payment.copy()
            meta_payment['paypal'] = request.data

            serializer = UserSubscriptionSerializerMeta(
                user_subscription, data={"meta_payment": meta_payment}, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET', 'POST'], url_path=r'first_data', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_firstdata(self, request):
        # api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        if request.method == "GET":
            payment_data = user_subscription.meta_payment.get("first_data", {})
            
            return Response(payment_data, status=status.HTTP_200_OK)
        else:
            meta_payment = user_subscription.meta_payment.copy()
            meta_payment['first_data'] = request.data

            serializer = UserSubscriptionSerializerMeta(
                user_subscription, data={"meta_payment": meta_payment}, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET', 'POST'], url_path=r'stripe', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_stripe(self, request):
        # api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        if request.method == "GET":
            payment_data = user_subscription.meta_payment.get("stripe", {})
            
            return Response(payment_data, status=status.HTTP_200_OK)
        else:
            meta_payment = user_subscription.meta_payment.copy()
            meta_payment['stripe'] = request.data

            serializer = UserSubscriptionSerializerMeta(
                user_subscription, data={"meta_payment": meta_payment}, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET', 'POST'], url_path=r'pay_mongo', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_paymongo(self, request):
        # api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        if request.method == "GET":
            payment_data = user_subscription.meta_payment.get("pay_mongo", {})
            
            return Response(payment_data, status=status.HTTP_200_OK)
        else:
            
            meta_payment = user_subscription.meta_payment.copy()
            meta_payment['pay_mongo'] = request.data

            serializer = UserSubscriptionSerializerMeta(
                user_subscription, data={"meta_payment": meta_payment}, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET', 'POST'], url_path=r'direct_payment', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_direct_payment(self, request):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        if request.method == "GET":
            payment_data = user_subscription.meta_payment.get("direct_payment", {})
            
            return Response(payment_data, status=status.HTTP_200_OK)
        else: 
            text = request.data['text']
            data = json.loads(text)

            if 'accounts' in data:
                for account_number, account_info in data['accounts'].items():
                    if account_number in request.data and request.data[account_number]:
                        if account_number in request.data:
                            image = request.data[account_number]
                            image_path = default_storage.save(
                                f'/{user_subscription.id}/payment/direct_payment/{image.name}', ContentFile(image.read()))
                            print(image_path)
                            data['accounts'][account_number]['image'] = image_path

            meta_payment = user_subscription.meta_payment.copy()
            meta_payment['direct_payment'] = data
            
            serializer = UserSubscriptionSerializerMeta(
                user_subscription, data={"meta_payment": meta_payment}, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            user_subscription = serializer.save()

            return Response(UserSubscriptionSerializerMeta(user_subscription).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'update_logistic', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_logistic(self, request):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        serializer = UserSubscriptionSerializerMeta(
            user_subscription, data={"meta_logistic": request.data}, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'language', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_language(self, request):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        return Response(user_subscription.lang, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'language/update', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_language(self, request):
        print("---------------")
        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        language, = getdata(request, ('language',))
        Verify.language_supported(language)
            
        user_subscription.lang = language
        user_subscription.save()
        print(user_subscription.lang)
        return Response(UserSubscriptionSerializerSimplify(user_subscription).data, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['PUT'], url_path=r'update_note', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_note(self, request):
        delivery_note, special_note, confirmation_note = getdata(request, ('delivery_note',"special_note", "confirmation_note"))

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        user_subscription.meta['delivery_note']=delivery_note
        user_subscription.meta['special_note']=special_note
        user_subscription.meta['confirmation_note']=confirmation_note

        user_subscription.save()

        return Response(UserSubscriptionSerializerMeta(user_subscription).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'admin_search_list', permission_classes=(IsAdminUser,))
    @api_error_handler
    def search_user_subscription(self, request):
        search_column = request.query_params.get('search_column')
        keyword = request.query_params.get('keyword')
        kwargs = { search_column + '__icontains': keyword }

        queryset = UserSubscription.objects.all().order_by('id')

        if search_column != 'undefined' and keyword != 'undefined':
            queryset = queryset.filter(**kwargs)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'facebook_pages', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_user_subscription_facebook_pages(self, request):
        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        
        return Response(FacebookPageSerializer(user_subscription.facebook_pages.all(),many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'v2/bind_facebook_pages', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def bind_user_facebook_pages(self, request):

        token, = getdata(request,('accessToken',), required=True)

        api_user = Verify.get_seller_user(request)
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        status_code, response = api_fb_get_me_accounts(token)

        if status_code != 200:
            raise ApiVerifyError("api_fb_get_accounts_from_user error")

        for item in response['data']:
            page_token = item['access_token']
            page_id = item['id']
            page_name = item['name']

            status_code, picture_data = api_fb_get_page_picture(
                page_token=page_token, page_id=page_id, height=100, width=100)
            
            page_image = item['image'] = picture_data['data']['url'] if status_code == 200 else None

            if FacebookPage.objects.filter(page_id=page_id).exists():
                facebook_page = FacebookPage.objects.get(page_id=page_id)
                facebook_page.name = page_name
                facebook_page.token = page_token
                facebook_page.token_update_at = datetime.now()
                facebook_page.image = page_image
                facebook_page.save()
            else:
                facebook_page = FacebookPage.objects.create(
                    page_id=page_id, name=page_name, token=page_token, token_update_at=datetime.now(), image=page_image)
                facebook_page.save()

            if facebook_page not in api_user_user_subscription.facebook_pages.all():
                api_user_user_subscription.facebook_pages.add(facebook_page)

        return Response(FacebookPageSerializer(api_user_user_subscription.facebook_pages.all(),many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'youtube_channels', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_user_subscription_youtube_channel(self, request):
        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        
        return Response(YoutubeChannelSerializer(user_subscription.youtube_channels.all(),many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'bind_youtube_channels', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def bind_youtube_channels_frontend(self, request):
        google_user_code, redirect_uri = getdata(request,("code", "redirect_uri"))
        api_user = Verify.get_seller_user(request)    
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        print(request.META["HTTP_ORIGIN"])
        response = requests.post(
                url="https://accounts.google.com/o/oauth2/token",
                data={
                    "code": google_user_code,
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER,
                    "redirect_uri": request.META['HTTP_ORIGIN'],
                    # "redirect_uri": settings.WEB_SERVER_URL + "/bind_youtube_channels_callback",
                    "grant_type": "authorization_code"
                }
            )


        if not response.status_code / 100 == 2:
            print(response.json())
            raise ApiCallerError('get google token fail')

        access_token = response.json().get("access_token")
        refresh_token = response.json().get("refresh_token")

        status_code, response = api_youtube_get_list_channel_by_token(access_token)

        if status_code != 200:
            raise ApiCallerError("get youtube channels error")
        
        if not response.get("items"):
            raise ApiCallerError("not channel found in this account.")
        #TODO handle next page token
        for item in response['items']:

            channel_etag = item['etag']
            channel_id = item['id']
            snippet = item['snippet']
            title = snippet['title']
            picture = snippet['thumbnails']['default']['url']
            
            if YoutubeChannel.objects.filter(channel_id=channel_id).exists():
                youtube_channel = YoutubeChannel.objects.get(channel_id=channel_id)
                youtube_channel.name = title
                youtube_channel.token = access_token
                youtube_channel.refresh_token = refresh_token
                youtube_channel.token_update_at = datetime.now()
                youtube_channel.image = picture
                youtube_channel.save()
            else:
                youtube_channel = YoutubeChannel.objects.create(
                    channel_id=channel_id, 
                    name=title, 
                    token=access_token, 
                    refresh_token=refresh_token,
                    token_update_at=datetime.now(), 
                    image=picture
                )
                youtube_channel.save()

            if youtube_channel not in api_user_user_subscription.youtube_channels.all():
                api_user_user_subscription.youtube_channels.add(youtube_channel)

        return Response({}, status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['GET'], url_path=r'v2/bind_youtube_channels_callback', permission_classes=())
    @api_error_handler
    def bind_youtube_channels(self, request):

        state,google_user_code = getparams(request,("state","code"), with_user=False)
        state = json.loads(state)
        redirect_uri, redirect_route, callback_uri, user_subscription_id = state.get('redirect_uri'),state.get('redirect_route'),state.get('callback_uri'), state.get('user_subscription_id')

        api_user_user_subscription = Verify.get_user_subscription(user_subscription_id)

        response = requests.post(
                url="https://accounts.google.com/o/oauth2/token",
                data={
                    "code": google_user_code,
                    "client_id": "536277208137-okgj3vg6tskek5eg6r62jis5didrhfc3.apps.googleusercontent.com",
                    "client_secret": "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",
                    "redirect_uri": callback_uri,
                    "grant_type": "authorization_code"
                }
            )


        if not response.status_code / 100 == 2:
            print(response.json())
            raise ApiCallerError('get google token fail')

        access_token = response.json().get("access_token")
        refresh_token = response.json().get("refresh_token")

        status_code, response = api_youtube_get_list_channel_by_token(access_token)

        if status_code != 200:
            raise ApiCallerError("get youtube channels error")

        #TODO handle next page token
        for item in response['items']:

            channel_etag = item['etag']
            channel_id = item['id']
            snippet = item['snippet']
            title = snippet['title']
            picture = snippet['thumbnails']['default']['url']
            
            if YoutubeChannel.objects.filter(channel_id=channel_id).exists():
                youtube_channel = YoutubeChannel.objects.get(channel_id=channel_id)
                youtube_channel.name = title
                youtube_channel.token = access_token
                youtube_channel.refresh_token = refresh_token
                youtube_channel.token_update_at = datetime.now()
                # youtube_channel.token_update_by = api_user.google_info['id']
                youtube_channel.image = picture
                youtube_channel.save()
            else:
                youtube_channel = YoutubeChannel.objects.create(
                    channel_id=channel_id, name=title, token=access_token, refresh_token=refresh_token, token_update_at=datetime.now(), image=picture)
                youtube_channel.save()

            if youtube_channel not in api_user_user_subscription.youtube_channels.all():
                api_user_user_subscription.youtube_channels.add(youtube_channel)

        redirect = HttpResponseRedirect(redirect_to=redirect_uri+'#/'+redirect_route)
        return redirect

    @action(detail=False, methods=['GET'], url_path=r'instagram_profiles', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_user_subscription_instagram_profile(self, request):
        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        
        return Response(InstagramProfileSerializer(user_subscription.instagram_profiles.all(),many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'v2/bind_instagram_profiles', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def bind_user_instagram_profiles(self, request):
        token, = getdata(request,('accessToken',), required=True)

        api_user = Verify.get_seller_user(request)
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        status_code, response = api_fb_get_me_accounts(token)

        if status_code != 200:
            raise ApiVerifyError("api_fb_get_accounts_from_user error")

        for item in response['data']:
            page_token = item['access_token']
            page_id = item['id']
            page_name = item['name']

            status_code, business_profile_response = api_fb_get_page_business_profile(page_token, page_id)
            print(business_profile_response)
            if status_code != 200:
                print('get profile error')
                continue

            business_id = business_profile_response.get("instagram_business_account",{}).get("id")
            
            if not business_id:
                print('no business id')
                continue

            status_code, profile_info_response = api_ig_get_profile_info(page_token, business_id)
            profile_name = profile_info_response.get('name')
            profile_pricure = profile_info_response.get('profile_picture_url')

            if InstagramProfile.objects.filter(business_id=business_id).exists():
                instagram_profile = InstagramProfile.objects.get(business_id=business_id)
                instagram_profile.name = profile_name
                instagram_profile.token = page_token
                instagram_profile.token_update_at = datetime.now()
                # instagram_profile.token_update_by = api_user.facebook_info['id']
                instagram_profile.image = profile_pricure
                instagram_profile.save()
            else:
                instagram_profile = InstagramProfile.objects.create(
                    business_id=business_id, name=profile_name, token=page_token, token_update_at=datetime.now(), image=profile_pricure)
                instagram_profile.save()

            if instagram_profile not in api_user_user_subscription.instagram_profiles.all():
                api_user_user_subscription.instagram_profiles.add(instagram_profile)

        return Response(FacebookPageSerializer(api_user_user_subscription.facebook_pages.all(),many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'dealer_search_list', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def dealer_search_list_subscriber(self, request):

        api_user, search_column, keyword = getparams(request,('search_column','keyword'),with_user=True, seller=True)
        dealer_user_subscription = Verify.get_dealer_user_subscription_from_api_user(api_user)

        queryset = dealer_user_subscription.subscribers.all()

        if search_column and keyword and search_column!='undefined' and keyword != 'undefined': 
            kwargs = { search_column + '__icontains': keyword }
            queryset = queryset.filter(**kwargs)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSubscriptionSerializerDealerList(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = UserSubscriptionSerializerDealerList(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'dealer_retrieve', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def dealer_retrieve_subscriber(self, request, pk=None):
        api_user = Verify.get_seller_user(request)
        dealer_user_subscription = Verify.get_dealer_user_subscription_from_api_user(api_user)
        user_subscription = Verify.get_user_subscription_from_dealer_user_subscription(dealer_user_subscription,pk)

        return Response(UserSubscriptionSerializerForDealerRetrieve(user_subscription).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT'], url_path=r'unsubscribe_facebook_page', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def unsubscribe_facebook_page(self, request):
        facebook_page_id, = getdata(request,("facebook_page_id",))
        api_user = Verify.get_seller_user(request)       
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        
        try:
            facebook_page = api_user_user_subscription.facebook_pages.filter(id=facebook_page_id)
            facebook_page.delete()
        except:
            raise ApiCallerError("no facebook page found")
        return Response({"delete": True}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT'], url_path=r'unsubscribe_youtube_channel', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def unsubscribe_youtube_channel(self, request):
        youtube_channel_id, = getdata(request,("youtube_channel_id",))
        api_user = Verify.get_seller_user(request)       
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        
        try:
            youtube_channel = api_user_user_subscription.youtube_channels.filter(id=youtube_channel_id)
            youtube_channel.delete()
        except:
            raise ApiCallerError("no facebook page found")
        return Response({"delete": True}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT'], url_path=r'unsubscribe_instagram_profile', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def unsubscribe_instagram_profile(self, request):
        instagram_profile_id, = getdata(request,("instagram_profile_id",))
        api_user = Verify.get_seller_user(request)       
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        
        try:
            instagram_profile = api_user_user_subscription.instagram_profiles.filter(id=instagram_profile_id)
            instagram_profile.delete()
        except:
            raise ApiCallerError("no facebook page found")
        return Response({"delete": True}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT'], url_path=r'update_currency', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_currency(self, request):
        api_user, currency, = getparams(request, ("currency",))     
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        
        api_user_user_subscription.currency = currency
        api_user_user_subscription.save()
        return Response(api_user_user_subscription.currency, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'get_currency', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_currency(self, request, pk=None):
        api_user = Verify.get_seller_user(request)    
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        
        return Response(api_user_user_subscription.currency, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer/list', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_buyer_list(self, request, pk=None):
        api_user = Verify.get_seller_user(request)    
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        buyer_list = get_user_subscription_buyer_list(api_user_user_subscription.id)
        return Response(buyer_list, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'me', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_seller_information(self, request, pk=None):
        api_user = Verify.get_seller_user(request)    
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        buyer_information = {
            'plan': api_user_user_subscription.type,
            'name': api_user_user_subscription.name,
            'phone': api_user.phone,
            'email': api_user.email,
            'period': api_user_user_subscription.expired_at.strftime("%Y/%m/%d, %H:%M:%S"),
            'country_code': api_user_user_subscription.meta_country.get('activated_country')[0],
            'currency': api_user_user_subscription.currency
        }
        return Response(buyer_information, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'plan', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def plan_information(self, request, pk=None):
        api_user = Verify.get_seller_user(request)    
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        plan_information = {
            'plan': api_user_user_subscription.type,
            'id': api_user_user_subscription.id,
            'join_time': api_user_user_subscription.created_at.strftime("%d %b %Y, %H:%M"),
            'period': api_user_user_subscription.expired_at.strftime("%d %b %Y, %H:%M")
        }
        return Response(plan_information, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['POST'], url_path=r'upgrade/intent')
    @api_error_handler
    def upgrade_intent(self, request):
        email, plan, period = lib.util.getter.getdata(request, ("email", "plan", "period"), required=True)
        api_user = Verify.get_seller_user(request)    
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(api_user_user_subscription.meta_country.get('activated_country')[0])
        subscription_plan = country_plan.get_plan(plan)

        kwargs = {'email':email, 'plan':plan, 'period':period, 'country_plan':country_plan, 'subscription_plan':subscription_plan}
        kwargs = rule.rule_checker.user_subscription_rule_checker.UpgradeIntentDataRuleChecker.check(**kwargs)

        email = kwargs.get('email')
        amount = kwargs.get('amount')

        stripe.api_key = settings.STRIPE_API_KEY  
        try:
            intent = stripe.PaymentIntent.create( amount=int(amount*100), currency=country_plan.currency, receipt_email = email)
        except Exception:
            raise ApiCallerError("invalid email")

        return Response({
            "client_secret":intent.client_secret,
            "payment_amount":amount,
            "user_plan":plan
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'upgrade')
    @api_error_handler
    def upgrade(self, request):
        email, password, plan, period, intentSecret, promoCode, timezone = lib.util.getter.getdata(request,("email", "password", "plan", "period", "intentSecret", "promoCode", "timezone"), required=False)
        api_user = Verify.get_seller_user(request)    
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        payment_intent_id = intentSecret[:27]
        stripe.api_key = settings.STRIPE_API_KEY
        paymentIntent = stripe.PaymentIntent.retrieve(payment_intent_id)

        kwargs = {'paymentIntent':paymentIntent,'email':email,'plan':plan,'period':period, 'promoCode':promoCode}
        kwargs = rule.rule_checker.user_rule_checker.RegistrationPaymentCompleteChecker.check(**kwargs)

        try:
            country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(api_user_user_subscription.meta_country.get('activated_country')[0])
            subscription_plan = country_plan.get_plan(plan)

            kwargs.update({'country_plan':country_plan, 'subscription_plan':subscription_plan})
            kwargs = rule.rule_checker.user_rule_checker.RegistrationRequireRefundChecker.check(kwargs)
        except Exception:
            #TODO refund
            print('require refund')
            raise ApiVerifyError('data invalid')

        email = kwargs.get('email')
        now = datetime.now(pytz.timezone(timezone)) if timezone in pytz.common_timezones else datetime.now()
        expired_at = now+timedelta(days=90) if period == "quarter" else now+timedelta(days=365)

        UserSubscription.objects.filter(email=email).update(
            type=plan, 
            expired_at=expired_at, 
            started_at=now, 
            user_plan= {"activated_platform" : ["facebook","youtube","instagram"]}, 
            meta_country={ 'activated_country': [country_code] },
            meta = {"stripe payment intent":intentSecret}
        )
        
        ret = {
            "Email": email,
            "Your Plan": subscription_plan.get('text'),
            "Subscription Period": period,
            "Subscription End Date": expired_at.strftime("%d %B %Y %H:%M"),
            "Receipt": paymentIntent.charges.get('data')[0].get('receipt_url')
        }

        return Response(ret, status=status.HTTP_200_OK)