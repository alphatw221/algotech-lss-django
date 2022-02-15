import re
from sys import platform
from django.http.response import HttpResponse
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.models.user.user import User, UserSerializer
from api.models.youtube.youtube_channel import YoutubeChannel
from api.utils.common.verify import ApiVerifyError
from api.utils.error_handle.error.api_error import ApiCallerError
from api.views.user._user import facebook_login_helper, google_login_helper, google_fast_login_helper
from backend.api.facebook.user import api_fb_get_accounts_from_user
from backend.api.facebook.page import api_fb_get_page_picture
from backend.api.youtube.channel import api_youtube_get_list_channel_by_token
from rest_framework.response import Response
from rest_framework import status
from api.models.facebook.facebook_page import FacebookPage
from datetime import datetime
from api.models.user.user_subscription import UserSubscription, UserSubscriptionSerializerSimplify

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.common.verify import Verify
platform_info_dict={'facebook':'facebook_info', 'youtube':'youtube_info', 'instagram':'instagram_info'}

class UserViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filterset_fields = []

    @action(detail=False, methods=['POST'], url_path=r'customer_login')
    @api_error_handler
    def customer_login(self, request, pk=None):
        return facebook_login_helper(request, user_type='customer')

    @action(detail=False, methods=['POST'], url_path=r'user_login')
    @api_error_handler
    def user_login(self, request, pk=None):
        return facebook_login_helper(request, user_type='user')

    

    @action(detail=False, methods=['GET'], url_path=r'google_user_callback')
    @api_error_handler
    def google_user_callback(self, request):
        return google_fast_login_helper(request, user_type='user')



    @action(detail=False, methods=['GET'], url_path=r'google_customer_login_callback')
    @api_error_handler
    def google_customer_login_callback(self, request):
        return google_login_helper(request, user_type='customer')

    @action(detail=False, methods=['GET'], url_path=r'google_user_login_callback')
    @api_error_handler
    def google_user_login_callback(self, request):
        return google_login_helper(request, user_type='user')



    @api_error_handler
    @action(detail=False, methods=['GET'], url_path=r'facebook_pages')
    def get_facebook_pages_by_client(self, request):

        api_user = request.user.api_users.get(type='user')

        if not api_user:
            raise ApiVerifyError("no user found")
        elif api_user.status != "valid":
            raise ApiVerifyError("not activated user")

        status_code, response = api_fb_get_accounts_from_user(
            user_token=api_user.facebook_info['token'], user_id=api_user.facebook_info['id'])

        if status_code != 200:
            raise ApiVerifyError("api_fb_get_accounts_from_user error")

        for item in response['data']:
            page_token = item['access_token']
            page_id = item['id']
            page_name = item['name']
            status_code, picture_data = api_fb_get_page_picture(
                page_token=page_token, page_id=page_id, height=100, width=100)
            item['image'] = picture_data['data']['url'] if status_code == 200 else None
            
            if FacebookPage.objects.filter(page_id=page_id).exists():
                facebook_page = FacebookPage.objects.get(page_id=page_id)
                facebook_page.token = page_token
                facebook_page.token_update_at = datetime.now()
                facebook_page.token_update_by = api_user.facebook_info['id']
                facebook_page.image = item['image']
                facebook_page.save()
            else:
                facebook_page = FacebookPage.objects.create(
                    page_id=page_id, name=page_name, token=page_token, token_update_at=datetime.now(), token_update_by=api_user.facebook_info['id'], image=item['image'])
                facebook_page.save()

            user_subscriptions = facebook_page.user_subscriptions.all()
            item['user_subscription'] = UserSubscriptionSerializerSimplify(
                user_subscriptions[0]).data if user_subscriptions else None

            del item['access_token']
            del item['category_list']
            del item['tasks']
            item['id'] = facebook_page.id
        del response['paging']
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'facebook_pages')
    def get_facebook_pages_by_server(self, request, pk=None):

        if not User.objects.filter(id=pk).exists():
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)

        api_user = User.objects.get(id=pk)
        if api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        status_code, response = api_fb_get_accounts_from_user(
            user_token=api_user.facebook_info['token'], user_id=api_user.facebook_info['id'])

        if status_code != 200:
            return Response({'message': 'api_fb_get_accounts_from_user error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        for item in response['data']:
            page_token = item['access_token']
            page_id = item['id']
            page_name = item['name']
            status_code, picture_data = api_fb_get_page_picture(
                page_token=page_token, page_id=page_id, height=100, width=100)
            item['image'] = picture_data['data']['url'] if status_code == 200 else None
            if FacebookPage.objects.filter(page_id=page_id).exists():
                FacebookPage.objects.filter(page_id=page_id).update(token=page_token, token_update_at=datetime.now(
                ), token_update_by=api_user.facebook_info['id'], image=item['image'])
            else:
                FacebookPage.objects.create(
                    page_id=page_id, name=page_name, token=page_token, token_update_at=datetime.now(), token_update_by=api_user.facebook_info['id'], image=item['image'])

        return Response(response, status=status.HTTP_200_OK)

    @api_error_handler
    @action(detail=False, methods=['GET'], url_path=r'youtube_channels')
    def get_youtube_channels(self, request):

        api_user = Verify.get_seller_user(request)

        google_token = api_user.google_info.get['access_token']
        
        if not google_token:
            raise ApiVerifyError('no google oauth token')

        status_code, response = api_youtube_get_list_channel_by_token(google_token)

        if status_code != 200:
            raise ApiCallerError("get youtube channels error")

        #TODO handle next page token
        for item in response['items']:

            channel_etag = item['etag']
            channel_id = item['id']
            snippet = item['snippet']

            title = snippet['title']
            picture = snippet['thumbnails']['default']['url']
            
            youtube_channel = YoutubeChannel.objects.update_or_create(
                    channel_id=channel_id, name=title, token=google_token, token_update_at=datetime.now(), token_update_by=api_user.youtube_info['id'], image=picture)

        return Response(response, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'profile_image', permission_classes=(IsAuthenticated,))
    def get_profile_image(self, request, pk=None):

        platform_name = request.query_params.get('platform_name')
        if not platform_name in platform_info_dict:
            raise ApiVerifyError('not support platform')

        picture = ""
        auth_user = request.user
        if auth_user.api_users.filter(type='user').exists():
            api_user = auth_user.api_users.get(type='user')
            picture = getattr(api_user,platform_info_dict[platform_name]).get('picture','')
        elif auth_user.api_users.filter(type='customer').exists():
            api_user = auth_user.api_users.get(type='customer')
            picture = getattr(api_user,platform_info_dict[platform_name]).get('picture','')

        return Response(picture, status=status.HTTP_200_OK)