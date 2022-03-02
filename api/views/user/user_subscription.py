from platform import platform
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.models.user.user import User
from api.models.user.user_subscription import UserSubscription, UserSubscriptionSerializer, UserSubscriptionSerializerMeta, UserSubscriptionSerializerSimplify, UserSubscriptionSerializerCreate
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from datetime import datetime
from api.utils.common.common import getdata
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
    permission_classes = (IsAuthenticated,)
    queryset = UserSubscription.objects.all().order_by('id')
    serializer_class = UserSubscriptionSerializer
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

    @action(detail=False, methods=['GET'], url_path=r'get_meta')
    @api_error_handler
    def get_meta(self, request):
        api_user, platform_name, platform_id = getparams(request, ('platform_name', 'platform_id'), with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        user_subscription = Verify.get_user_subscription_from_platform(platform)

        serializer = UserSubscriptionSerializerMeta(user_subscription)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'update_hitpay')
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

    @action(detail=False, methods=['POST'], url_path=r'update_paypal')
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

    @action(detail=False, methods=['POST'], url_path=r'update_firstdata')
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

    @action(detail=False, methods=['POST'], url_path=r'update_stripe')
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

    @action(detail=False, methods=['POST'], url_path=r'update_direct_payment', parser_classes=(MultiPartParser,))
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

    @action(detail=False, methods=['POST'], url_path=r'update_logistic')
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


    @action(detail=False, methods=['PUT'], url_path=r'update_language')
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

    
    @action(detail=False, methods=['PUT'], url_path=r'update_note')
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
    