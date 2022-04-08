from calendar import month
import json
from math import perm
import re, pendulum
from sys import platform
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from pymysql import NULL
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.models.campaign.campaign import YoutubeCampaignSerializer
from api.models.instagram.instagram_profile import InstagramProfile, InstagramProfileSerializer
from api.models.user.user import User, UserSerializer
from api.models.youtube.youtube_channel import YoutubeChannel, YoutubeChannelSerializer
from api.utils.common.common import getdata, getparams
from api.utils.common.verify import ApiVerifyError
from api.utils.error_handle.error.api_error import ApiCallerError
from api.views.user._user import facebook_login_helper, google_login_helper, google_authorize_helper
from backend.api.facebook.user import api_fb_get_accounts_from_user
from backend.api.facebook.page import api_fb_get_page_picture
from backend.api.youtube.channel import api_youtube_get_list_channel_by_token
from rest_framework.response import Response
from rest_framework import status
from api.models.facebook.facebook_page import FacebookPage, FacebookPageSerializer
from datetime import datetime, timedelta
from api.models.user.user_subscription import UserSubscription, UserSubscriptionSerializerSimplify
from django.contrib.auth.models import User as AuthUser
from rest_framework_simplejwt.tokens import RefreshToken

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.common.verify import Verify
from rest_framework.pagination import PageNumberPagination
from backend.api.google.user import api_google_get_userinfo
from django.conf import settings
import string
import random
from api.models.user.user_subscription import UserSubscription
from lss.views.custom_jwt import CustomTokenObtainPairSerializer
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from backend.api.facebook.page import api_fb_get_page_business_profile
from backend.api.instagram.profile import api_ig_get_profile_info
# from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth import authenticate

import stripe
platform_info_dict={'facebook':'facebook_info', 'youtube':'youtube_info', 'instagram':'instagram_info', 'google':'google_info'}


class UserPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class UserViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filterset_fields = []
    pagination_class = UserPagination

    #facebook
    @action(detail=False, methods=['POST'], url_path=r'customer_login')
    @api_error_handler
    def customer_login(self, request, pk=None):
        return facebook_login_helper(request, user_type='customer')

    #facebook
    @action(detail=False, methods=['POST'], url_path=r'user_login')
    @api_error_handler
    def user_login(self, request, pk=None):
        return facebook_login_helper(request, user_type='user')

    
    #google
    @action(detail=False, methods=['POST'], url_path=r'customer_google_login')
    @api_error_handler
    def customer_google_login(self, request, pk=None):
        user_type='buyer'
        token = request.data.get('token')
        identity_info = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER)

        google_id, google_name, google_picture, email = identity_info["sub"], identity_info["name"], identity_info["picture"], identity_info["email"]

        api_user_exists = User.objects.filter(
            email=email, type=user_type).exists()
        auth_user_exists = AuthUser.objects.filter(email=email).exists()

        scenario1 = api_user_exists and auth_user_exists
        scenario2 = api_user_exists and not auth_user_exists
        scenario3 = not api_user_exists and auth_user_exists

        # scenario4: both don't exists

        if scenario1:
            api_user = User.objects.get(email=email, type=user_type)
            auth_user = AuthUser.objects.get(email=email)
            if not api_user.auth_user:
                api_user.auth_user=auth_user
        elif scenario2:
            api_user = User.objects.get(email=email, type=user_type)
            auth_user = AuthUser.objects.create_user(
                google_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
            api_user.auth_user = auth_user
        elif scenario3:
            auth_user = AuthUser.objects.get(email=email)
            api_user = User.objects.create(
                name=google_name, email=email, type=user_type, status='new', auth_user=auth_user)
        else:  # scenario4
            auth_user = AuthUser.objects.create_user(
                google_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
            api_user = User.objects.create(
                name=google_name, email=email, type=user_type, status='new', auth_user=auth_user)

        if user_type == 'user' and api_user.status != 'valid':
            raise ApiVerifyError('account not activated')

        api_user.google_info["id"] = google_id
        api_user.google_info["name"] = google_name
        api_user.google_info["picture"] = google_picture


        auth_user.last_login = datetime.now()
        auth_user.save()
        api_user.save()


        refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

        ret = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return ret
        

    #google
    @action(detail=False, methods=['POST'], url_path=r'user_google_login')
    @api_error_handler
    def user_google_login(self, request, pk=None):
        user_type='user'
        google_user_code = request.data.get('code')
        response = requests.post(
                url="https://accounts.google.com/o/oauth2/token",
                data={
                    "code": google_user_code,
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER,
                    # "redirect_uri": 'http://localhost:8000/google-redirect',
                    "redirect_uri": settings.WEB_SERVER_URL + "/google-redirect",
                    "grant_type": "authorization_code"
                }
            )

        if not response.status_code / 100 == 2:
            print(response.json())
            raise ApiCallerError('get google token fail')

        access_token = response.json().get("access_token")
        refresh_token = response.json().get("refresh_token")

        code, response = api_google_get_userinfo(access_token)

        if code / 100 != 2:
            print(response)
            raise ApiCallerError("google user token invalid")

        google_id, google_name, google_picture, email = response["id"], response["name"], response["picture"], response["email"]

        api_user_exists = User.objects.filter(
            email=email, type=user_type).exists()
        auth_user_exists = AuthUser.objects.filter(email=email).exists()

        scenario1 = api_user_exists and auth_user_exists
        scenario2 = api_user_exists and not auth_user_exists
        scenario3 = not api_user_exists and auth_user_exists

        # scenario4: both don't exists

        if scenario1:
            api_user = User.objects.get(email=email, type=user_type)
            auth_user = AuthUser.objects.get(email=email)
            if not api_user.auth_user:
                api_user.auth_user=auth_user
        elif scenario2:
            api_user = User.objects.get(email=email, type=user_type)
            auth_user = AuthUser.objects.create_user(
                google_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
            api_user.auth_user = auth_user
        elif scenario3:
            auth_user = AuthUser.objects.get(email=email)
            api_user = User.objects.create(
                name=google_name, email=email, type=user_type, status='new', auth_user=auth_user)
        else:  # scenario4
            auth_user = AuthUser.objects.create_user(
                google_name, email, ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8)))
            api_user = User.objects.create(
                name=google_name, email=email, type=user_type, status='new', auth_user=auth_user)

        if user_type == 'user' and api_user.status != 'valid':
            raise ApiVerifyError('account not activated')

        api_user.google_info["access_token"] = access_token
        api_user.google_info['refresh_token'] = refresh_token
        api_user.google_info["id"] = google_id
        api_user.google_info["name"] = google_name
        api_user.google_info["picture"] = google_picture

        auth_user.last_login = datetime.now()
        auth_user.save()
        api_user.save()

        refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

        ret = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response(ret, status=status.HTTP_200_OK)



    @action(detail=False, methods=['GET'], url_path=r'google_authorize')
    @api_error_handler
    def google_authorize(self, request):
        return google_authorize_helper(request, user_type='user')



    @action(detail=False, methods=['GET'], url_path=r'google_customer_login_callback')
    @api_error_handler
    def google_customer_login_callback(self, request):
        return google_login_helper(request, user_type='customer')

    @action(detail=False, methods=['GET'], url_path=r'google_user_login_callback')
    @api_error_handler
    def google_user_login_callback(self, request):
        return google_login_helper(request, user_type='user')


    
    @action(detail=False, methods=['GET'], url_path=r'facebook_pages', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_facebook_pages(self, request):

        api_user = Verify.get_seller_user(request)
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        user_token = api_user.facebook_info.get('token')
        user_id = api_user.facebook_info.get('id')

        if not user_token or not user_id:
            raise ApiVerifyError('no facebook token or id')

        status_code, response = api_fb_get_accounts_from_user(
            user_token=user_token, user_id=user_id)

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
                facebook_page.token_update_by = api_user.facebook_info['id']
                facebook_page.image = page_image
                facebook_page.save()
            else:
                facebook_page = FacebookPage.objects.create(
                    page_id=page_id, name=page_name, token=page_token, token_update_at=datetime.now(), token_update_by=api_user.facebook_info['id'], image=page_image)
                facebook_page.save()

            if not facebook_page.user_subscriptions.all():
                api_user_user_subscription.facebook_pages.add(facebook_page)

            status_code, business_profile_response = api_fb_get_page_business_profile(facebook_page.token, facebook_page.page_id)
            print(business_profile_response)
            if status_code != 200:
                print('get profile error')
                continue

            business_id = business_profile_response.get("instagram_business_account",{}).get("id")
            
            if not business_id:
                print('no business id')
                continue

            status_code, profile_info_response = api_ig_get_profile_info(facebook_page.token, business_id)
            profile_name = profile_info_response.get('name')
            profile_pricure = profile_info_response.get('profile_picture_url')

            if InstagramProfile.objects.filter(business_id=business_id).exists():
                instagram_profile = InstagramProfile.objects.get(business_id=business_id)
                instagram_profile.name = profile_name
                instagram_profile.token = page_token
                instagram_profile.token_update_at = datetime.now()
                instagram_profile.token_update_by = api_user.facebook_info['id']
                instagram_profile.image = profile_pricure
                instagram_profile.save()
            else:
                instagram_profile = InstagramProfile.objects.create(
                    business_id=business_id, name=profile_name, token=page_token, token_update_at=datetime.now(), token_update_by=api_user.facebook_info['id'], image=profile_pricure)
                instagram_profile.save()

            if not instagram_profile.user_subscriptions.all():
                api_user_user_subscription.instagram_profiles.add(instagram_profile)



        return Response(FacebookPageSerializer(api_user_user_subscription.facebook_pages.all(), many = True).data, status=status.HTTP_200_OK)



        
        #---------
        # api_user = request.user.api_users.get(type='user')

        # if not api_user:
        #     raise ApiVerifyError("no user found")
        # elif api_user.status != "valid":
        #     raise ApiVerifyError("not activated user")

        # status_code, response = api_fb_get_accounts_from_user(
        #     user_token=api_user.facebook_info['token'], user_id=api_user.facebook_info['id'])

        # if status_code != 200:
        #     raise ApiVerifyError("api_fb_get_accounts_from_user error")

        # for item in response['data']:
        #     page_token = item['access_token']
        #     page_id = item['id']
        #     page_name = item['name']
        #     status_code, picture_data = api_fb_get_page_picture(
        #         page_token=page_token, page_id=page_id, height=100, width=100)
        #     item['image'] = picture_data['data']['url'] if status_code == 200 else None
            
        #     if FacebookPage.objects.filter(page_id=page_id).exists():
        #         facebook_page = FacebookPage.objects.get(page_id=page_id)
        #         facebook_page.name = page_name
        #         facebook_page.token = page_token
        #         facebook_page.token_update_at = datetime.now()
        #         facebook_page.token_update_by = api_user.facebook_info['id']
        #         facebook_page.image = item['image']
        #         facebook_page.save()
        #     else:
        #         facebook_page = FacebookPage.objects.create(
        #             page_id=page_id, name=page_name, token=page_token, token_update_at=datetime.now(), token_update_by=api_user.facebook_info['id'], image=item['image'])
        #         facebook_page.save()

        #     user_subscriptions = facebook_page.user_subscriptions.all()
        #     item['user_subscription'] = UserSubscriptionSerializerSimplify(
        #         user_subscriptions[0]).data if user_subscriptions else None

        #     del item['access_token']
        #     del item['category_list']
        #     del item['tasks']
        #     item['id'] = facebook_page.id
        # del response['paging']
        # return Response(response, status=status.HTTP_200_OK)

    # @action(detail=True, methods=['GET'], url_path=r'facebook_pages')
    # def get_facebook_pages_by_server(self, request, pk=None):

    #     if not User.objects.filter(id=pk).exists():
    #         return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)

    #     api_user = User.objects.get(id=pk)
    #     if api_user.status != "valid":
    #         return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

    #     status_code, response = api_fb_get_accounts_from_user(
    #         user_token=api_user.facebook_info['token'], user_id=api_user.facebook_info['id'])

    #     if status_code != 200:
    #         return Response({'message': 'api_fb_get_accounts_from_user error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #     for item in response['data']:
    #         page_token = item['access_token']
    #         page_id = item['id']
    #         page_name = item['name']
    #         status_code, picture_data = api_fb_get_page_picture(
    #             page_token=page_token, page_id=page_id, height=100, width=100)
    #         item['image'] = picture_data['data']['url'] if status_code == 200 else None
    #         if FacebookPage.objects.filter(page_id=page_id).exists():

    #             facebook_page = FacebookPage.objects.get(page_id=page_id)
    #             facebook_page.update(token=page_token, token_update_at=datetime.now(
    #             ), token_update_by=api_user.facebook_info['id'], image=item['image'])
    #         else:
    #             facebook_page = FacebookPage.objects.create(
    #                 page_id=page_id, name=page_name, token=page_token, token_update_at=datetime.now(), token_update_by=api_user.facebook_info['id'], image=item['image'])

    #         item['in_subscription']=True if len(facebook_page.user_subscriptions) else False

    #     return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'bind_youtube_channels_callback', permission_classes=())
    @api_error_handler
    def bind_youtube_channels(self, request):

        state,google_user_code = getparams(request,("state","code"), with_user=False)
        state = json.loads(state)
        redirect_uri, redirect_route, callback_uri, token = state.get('redirect_uri'),state.get('redirect_route'),state.get('callback_uri'), state.get('token')

        print(redirect_uri)
        print(redirect_route)
        print(callback_uri)

        auth_user_id = AccessToken(token).get('user_id')
        
        auth_user = AuthUser.objects.get(id=auth_user_id)
        api_user = auth_user.api_users.get(type='user')
        
        if not api_user:
            raise ApiVerifyError("user token error")

        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        response = requests.post(
                url="https://accounts.google.com/o/oauth2/token",
                data={
                    "code": google_user_code,
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER,
                    "redirect_uri": callback_uri,
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
                youtube_channel.token_update_by = api_user.google_info['id']
                youtube_channel.image = picture
                youtube_channel.save()
            else:
                youtube_channel = YoutubeChannel.objects.create(
                    channel_id=channel_id, name=title, token=access_token, refresh_token=refresh_token, token_update_at=datetime.now(), token_update_by=api_user.google_info['id'], image=picture)
                youtube_channel.save()

            if not youtube_channel.user_subscriptions.all():
                api_user_user_subscription.youtube_channels.add(youtube_channel)

        redirect = HttpResponseRedirect(redirect_to=redirect_uri+'#/'+redirect_route)
        return redirect
        # return Response(YoutubeChannelSerializer(api_user_user_subscription.youtube_channels.all(), many = True).data, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['GET'], url_path=r'youtube_channels', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_youtube_channels(self, request):

        api_user = Verify.get_seller_user(request)
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        return Response(YoutubeChannelSerializer(api_user_user_subscription.youtube_channels.all(), many = True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'instagram_profiles', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_instagram_profiles(self, request):

        api_user = Verify.get_seller_user(request)
        api_user_user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        return Response(InstagramProfileSerializer(api_user_user_subscription.instagram_profiles.all(), many = True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer_profile_images', permission_classes=(IsAuthenticated,))
    def get_buyer_profile_images(self, request):
        api_user = Verify.get_customer_user(request)
        pictures=[]
        for platform_name in ['facebook', 'youtube', 'instagram']:
            picture = getattr(api_user,platform_info_dict[platform_name]).get('picture')
            if picture:
                pictures.append(picture)
        return Response(pictures, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'profile_images', permission_classes=(IsAuthenticated,))
    def get_profile_image(self, request, pk=None):

        api_user = Verify.get_seller_user(request)
        pictures=[]
        for platform_name in ['facebook', 'youtube', 'instagram']:
            picture = getattr(api_user,platform_info_dict[platform_name]).get('picture')
            if picture:
                pictures.append(picture)
        return Response(pictures, status=status.HTTP_200_OK)


    
    @action(detail=False, methods=['POST'], url_path=r'create_valid_api_user', permission_classes=(IsAdminUser,))
    @api_error_handler
    def create_valid_api_user(self, request):

        name, email = getdata(request, ("name","email"))
        if not name or not email:
            raise ApiVerifyError('name and email must not be empty')

        if User.objects.filter(email=email, type='user').exists():
            api_user = User.objects.get(email=email, type='user')
            api_user.status='valid'
            api_user.save()
        else:
            api_user = User.objects.create(
                name=name, email=email, type='user', status='valid')

        return Response("ok", status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'search_list', permission_classes=(IsAdminUser,))
    @api_error_handler
    def search_api_user(self, request):
        search_column = request.query_params.get('search_column')
        keyword = request.query_params.get('keyword')
        kwargs = { search_column + '__icontains': keyword }

        queryset = User.objects.all().order_by('id')

        if search_column != 'undefined' and keyword != 'undefined':
            queryset = queryset.filter(**kwargs)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.dat

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'register_free_trial', permission_classes=())
    @api_error_handler
    def register_free_trial(self, request):
        email, plan = getdata(request, ("email", "plan"), required=True)
        firstName, lastName, contactNumber, password, country = getdata(request, ("firstName", "lastName", "contactNumber", "password", "country"), required=False)

        if plan != 'Free Trial':
            raise ApiVerifyError('plan option error')

        if AuthUser.objects.filter(email = email).exists() or User.objects.filter(email=email).exists():
            raise ApiVerifyError('email has already been used')

        expired_at = datetime.now()+timedelta(days=30)
        auth_user = AuthUser.objects.create_user(
            username=f'{firstName} {lastName}', email=email, password=password)
        
        user_subscription = UserSubscription.objects.create(
            name=f'{firstName} {lastName}', 
            status='valid', 
            expired_at=expired_at, 
            user_plan= {"activated_platform" : ["facebook"]}, 
            meta_country={ 'country': country },
            type='trial')
        
        api_user = User.objects.create(
            name=f'{firstName} {lastName}', email=email, type='user', status='valid', phone=contactNumber, auth_user=auth_user, user_subscription=user_subscription)
        

        ret = {
            "Email":email,
            "Password":password,
            "Plan":plan,
            "Subscription Period":"Monthly",
            "Expired At":expired_at.strftime("%m/%d/%Y, %H:%M:%S"),
            "Receipt":""
        }
        
        return Response(ret, status=status.HTTP_200_OK)



    @action(detail=False, methods=['POST'], url_path=r'validate_register', permission_classes=())
    @api_error_handler
    def validate_register_data(self, request):

        EARLY_BIRD_PROMO_CODE = 'test'
        STRIPE_API_KEY = "sk_test_51J2aFmF3j9D00CA0KABMZVKtOVnZNbBvM2hcokicJmfx8vvrmNyys5atEAcpp0Au2O3HtX0jz176my7g0ozbinof00RL4QAZrY" #TODO put it in settings

        email, plan, period = getdata(request, ("email", "plan", "period"), required=True)
        promoCode, = getdata(request, ("promoCode",), required=False)

        if promoCode and promoCode != EARLY_BIRD_PROMO_CODE:
            raise ApiVerifyError('invalid promo code')


        if AuthUser.objects.filter(email = email).exists() or User.objects.filter(email=email).exists():
            raise ApiVerifyError('email has already been used')
        
        if plan == 'Lite':
                amount = 1.00
        elif plan == 'Standard(USD 30.00/Month)':  
            if period == "Monthly":
                amount = 30.00
            else :
                amount = 90.00

            amount = amount*0.9 if promoCode == EARLY_BIRD_PROMO_CODE else amount
        elif plan =='Premium(USD 60.00/Month)':
            if period == "Monthly":
                amount = 60.00
            else :
                amount = 180.00
            amount = amount*0.9 if promoCode == EARLY_BIRD_PROMO_CODE else amount
        else:
            raise ApiVerifyError('plan option error')
        
        
        stripe.api_key = STRIPE_API_KEY  
        intent = stripe.PaymentIntent.create( amount=int(amount*100), currency="SGD",)
        
        return Response({
            "client_secret":intent.client_secret,
            "payment_amount":amount,
            "user_plan":plan
        }, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'register', permission_classes=())
    @api_error_handler
    def user_register(self, request):

        EARLY_BIRD_PROMO_CODE = 'test'
        STRIPE_API_KEY = "sk_test_51J2aFmF3j9D00CA0KABMZVKtOVnZNbBvM2hcokicJmfx8vvrmNyys5atEAcpp0Au2O3HtX0jz176my7g0ozbinof00RL4QAZrY" #TODO put it in settings

        email, password, plan, period, intentSecret = getdata(request,("email", "password", "plan", "period", "intentSecret"),required=True)
        firstName, lastName, contactNumber, country , promoCode = getdata(request, ("firstName", "lastName", "contactNumber", "country", "promoCode"), required=False)

        payment_intent_id = intentSecret[:27]
        stripe.api_key = STRIPE_API_KEY
        paymentIntent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if paymentIntent.status != "succeeded":
            raise ApiVerifyError('payment not succeeded')

        #last validation  (require refunds)
        # ------------------------------------------------------------------------------------
        if AuthUser.objects.filter(email = email).exists() or User.objects.filter(email=email).exists():
            raise ApiVerifyError('email has already been used')

        if plan == 'Lite':
            amount = 1.00
            subscription_type = "lite"

        elif plan == 'Standard(USD 30.00/Month)':  
            subscription_type = "standard"
            if period == "Monthly":
                amount = 30.00
            else :
                amount = 90.00

            amount = amount*0.9 if promoCode == EARLY_BIRD_PROMO_CODE else amount
        elif plan =='Premium(USD 60.00/Month)':
            subscription_type = "premium"
            if period == "Monthly":
                amount = 60.00
            else :
                amount = 180.00
            amount = amount*0.9 if promoCode == EARLY_BIRD_PROMO_CODE else amount
        else:
            raise ApiVerifyError('plan option error')

        if int(amount*100) != paymentIntent.amount:
            raise ApiVerifyError('payment amount error')
        #------------------------------------------------------------------------------------

        expired_at = datetime.now()+timedelta(days=30) if period == "Monthly" else datetime.now()+timedelta(days=60)
        
        auth_user = AuthUser.objects.create_user(
            username=f'{firstName} {lastName}', email=email, password=password)
        
        user_subscription = UserSubscription.objects.create(
            name=f'{firstName} {lastName}', 
            status='valid', 
            expired_at=expired_at, 
            user_plan= {"activated_platform" : ["facebook","youtube","instagram"]}, 
            meta_country={ 'country': country },
            meta = {"stripe payment intent":intentSecret},
            type=subscription_type)
        
        api_user = User.objects.create(
            name=f'{firstName} {lastName}', email=email, type='user', status='valid', phone=contactNumber, auth_user=auth_user, user_subscription=user_subscription)
        

        ret = {
            "Email":email,
            "Password":password,
            "Plan":plan,
            "Subscription Period":"Monthly",
            "Expired At":expired_at.strftime("%m/%d/%Y, %H:%M:%S"),
            "Receipt":paymentIntent.charges.get('data')[0].get('receipt_url')
        }
        
        return Response(ret, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'client_login')
    @api_error_handler
    def client_login(self, request):
        email, password = getdata(request, ("email","password"))
        
        username = User.objects.get(email=email).name

        auth_user = authenticate(username=username, password=password)

        if auth_user is not None:
            refresh = CustomTokenObtainPairSerializer.get_token(auth_user)
        else:
            return Response({"message": "Error User"}, status=status.HTTP_400_BAD_REQUEST)
        
        ret = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(ret, status=status.HTTP_200_OK)