from platform import platform
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.code.subscription_code_manager import SubscriptionCodeManager
from api.models.user.user import User
from api.models.user.user_subscription import UserSubscription, UserSubscriptionSerializer, UserSubscriptionSerializerMeta, UserSubscriptionSerializerSimplify, UserSubscriptionSerializerCreate
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from api.models.facebook.facebook_page import FacebookPage, FacebookPageSerializer
from api.models.youtube.youtube_channel import YoutubeChannel
from datetime import datetime
from api.utils.common.common import getdata
from backend.api.facebook.page import api_fb_get_page_picture
from backend.api.facebook.user import api_fb_get_me_accounts

from rest_framework.parsers import MultiPartParser
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from api.utils.common.verify import Verify, getparams
from api.utils.common.verify import ApiVerifyError

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.common.common import getparams

def verify_request(api_user, platform_name, platform_id):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    user_subscription = Verify.get_user_subscription_from_platform(platform)

    return platform, user_subscription


class UserSubscriptionPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


platform_dict = {'facebook': FacebookPage,
                 'youtube': YoutubeChannel}


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = UserSubscription.objects.all().order_by('id')
    serializer_class = UserSubscriptionSerializerSimplify
    filterset_fields = []
    pagination_class = UserSubscriptionPagination

    @action(detail=False, methods=['POST'], url_path=r'create_user_subscription', permission_classes=(IsAdminUser,))
    @api_error_handler
    def create_user_subscription(self, request):
        print(request.data)
        serializer = UserSubscriptionSerializerCreate(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = serializer.save()
        return Response(UserSubscriptionSerializer(user_subscription).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create_activate_code', permission_classes=(IsAdminUser,))
    @api_error_handler
    def create_activate_code(self, request):
        try:
            user_subscription_id, maximum_usage_count, interval = getdata(request, ('user_subscription_id','maximum_usage_count','interval'))
            # data = request.data
            # user_subscription_id, maximum_usage_count, interval = data.get('user_subscription_id', None), data.get('maximum_usage_count', None), data.get('interval', None)
            code = SubscriptionCodeManager.generate(user_subscription_id, maximum_usage_count, interval)
            return Response(code, status=status.HTTP_200_OK)
        except ApiVerifyError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['POST'], url_path=r'execute_activate_code', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def execute_activate_code(self, request):
        code, platform_name, platform_id = getdata(request,('activation_code','plarform_name','plarform_id'))
        subscription_page_data = SubscriptionCodeManager.execute(code, platform_name, platform_id)
        return Response(subscription_page_data, status=status.HTTP_200_OK)
        # try:
        #     data = request.data
        #     code, platform_name, platform_id = data['activation_code'], data['platform_name'], data['platform_id']
        #     subscription_page_data = SubscriptionCodeManager.execute(code, platform_name, platform_id)
        #     return Response(subscription_page_data, status=status.HTTP_200_OK)
        # except ApiVerifyError as e:
        #     return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'], url_path=r'add_platform', permission_classes=(IsAdminUser,))
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

    @action(detail=True, methods=['GET'], url_path=r'remove_platform', permission_classes=(IsAdminUser,))
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
        api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        user_subscription = Verify.get_user_subscription_from_platform(platform)

        serializer = UserSubscriptionSerializerMeta(user_subscription)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'update_hitpay', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_hitpay(self, request):
        api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        user_subscription = Verify.get_user_subscription_from_platform(platform)

        meta_payment = user_subscription.meta_payment
        meta_payment['hitpay'] = request.data

        serializer = UserSubscriptionSerializerMeta(
            user_subscription, data={"meta_payment": meta_payment}, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'update_paypal', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_paypal(self, request):
        api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        user_subscription = Verify.get_user_subscription_from_platform(platform)

        meta_payment = user_subscription.meta_payment
        meta_payment['paypal'] = request.data

        serializer = UserSubscriptionSerializerMeta(
            user_subscription, data={"meta_payment": meta_payment}, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'update_firstdata', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_firstdata(self, request):
        api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        user_subscription = Verify.get_user_subscription_from_platform(platform)

        meta_payment = user_subscription.meta_payment
        meta_payment['firstdata'] = request.data

        serializer = UserSubscriptionSerializerMeta(
            user_subscription, data={"meta_payment": meta_payment}, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'update_stripe', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_stripe(self, request):
        api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        user_subscription = Verify.get_user_subscription_from_platform(platform)

        meta_payment = user_subscription.meta_payment
        meta_payment['stripe'] = request.data

        serializer = UserSubscriptionSerializerMeta(
            user_subscription, data={"meta_payment": meta_payment}, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'update_direct_payment', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_direct_payment(self, request):
        api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        user_subscription = Verify.get_user_subscription_from_platform(platform)

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

        meta_payment = user_subscription.meta_payment
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
        api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        user_subscription = Verify.get_user_subscription_from_platform(platform)

        serializer = UserSubscriptionSerializerMeta(
            user_subscription, data={"meta_logistic": request.data}, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_subscription = serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['PUT'], url_path=r'update_language', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_language(self, request):
        api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)
        language, = getdata(request, ('language',))

        Verify.language_supported(language)
        platform = Verify.get_platform(api_user, platform_name, platform_id)
        user_subscription = Verify.get_user_subscription_from_platform(platform)

        user_subscription.lang = language
        user_subscription.save()

        return Response(UserSubscriptionSerializerSimplify(user_subscription).data, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['PUT'], url_path=r'update_note', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_note(self, request):
        api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)
        delivery_note, special_note, confirmation_note = getdata(request, ('delivery_note',"special_note", "confirmation_note"))

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        user_subscription = Verify.get_user_subscription_from_platform(platform)

        user_subscription.meta['delivery_note']=delivery_note
        user_subscription.meta['special_note']=special_note
        user_subscription.meta['confirmation_note']=confirmation_note

        user_subscription.save()

        return Response(UserSubscriptionSerializerMeta(user_subscription).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'search_list', permission_classes=(IsAdminUser,))
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

    @action(detail=True, methods=['POST'], url_path=r'bind_facebook_pages', permission_classes=())
    @api_error_handler
    def bind_user_facebook_pages(self, request, pk=None):
        token, = getdata(request,('accessToken',))
        api_user_user_subscription = Verify.get_user_subscription(pk)

        if not token:
            raise ApiVerifyError("please provide token")
        print(token)
        status_code, response = api_fb_get_me_accounts(token)

        print(response)

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

            if not facebook_page.user_subscriptions.all():
                api_user_user_subscription.facebook_pages.add(facebook_page)

            # status_code, business_profile_response = api_fb_get_page_business_profile(facebook_page.token, facebook_page.page_id)
            # print(business_profile_response)
            # if status_code != 200:
            #     print('get profile error')
            #     continue

            # business_id = business_profile_response.get("instagram_business_account",{}).get("id")
            
            # if not business_id:
            #     print('no business id')
            #     continue

            # status_code, profile_info_response = api_ig_get_profile_info(facebook_page.token, business_id)
            # profile_name = profile_info_response.get('name')
            # profile_pricure = profile_info_response.get('profile_picture_url')

            # if InstagramProfile.objects.filter(business_id=business_id).exists():
            #     instagram_profile = InstagramProfile.objects.get(business_id=business_id)
            #     instagram_profile.name = profile_name
            #     instagram_profile.token = page_token
            #     instagram_profile.token_update_at = datetime.now()
            #     instagram_profile.token_update_by = api_user.facebook_info['id']
            #     instagram_profile.image = profile_pricure
            #     instagram_profile.save()
            # else:
            #     instagram_profile = InstagramProfile.objects.create(
            #         business_id=business_id, name=profile_name, token=page_token, token_update_at=datetime.now(), token_update_by=api_user.facebook_info['id'], image=profile_pricure)
            #     instagram_profile.save()

            # if not instagram_profile.user_subscriptions.all():
            #     api_user_user_subscription.instagram_profiles.add(instagram_profile)

        return Response(FacebookPageSerializer(api_user_user_subscription.facebook_pages.all(),many=True).data, status=status.HTTP_200_OK)
