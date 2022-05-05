from calendar import month
from distutils.sysconfig import EXEC_PREFIX
from django.http import HttpResponseRedirect
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.code.password_code_manager import PasswordResetCodeManager
from api.models.instagram.instagram_profile import InstagramProfile, InstagramProfileSerializer
from api.models.user.user import User, UserSerializer, UserSerializerAccountInfo
from api.models.youtube.youtube_channel import YoutubeChannel, YoutubeChannelSerializer
from api.rule.rule_checker.user_rule_checker import DealerCreateAccountRuleChecker,AdminCreateAccountRuleChecker, SellerChangePasswordRuleChecker, SellerResetPasswordRuleChecker
from api.utils.common.common import getdata, getparams
from api.utils.common.verify import ApiVerifyError
from api.utils.error_handle.error.api_error import ApiCallerError
from api.views.user._user import facebook_login_helper, google_login_helper, google_authorize_helper
from automation.jobs.send_email_job import send_email_job
from backend.api.facebook.user import api_fb_get_accounts_from_user
from backend.api.facebook.page import api_fb_get_page_picture
from backend.api.youtube.channel import api_youtube_get_list_channel_by_token
from rest_framework.response import Response
from rest_framework import status
from api.models.facebook.facebook_page import FacebookPage, FacebookPageSerializer
from datetime import datetime, timedelta

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.common.verify import Verify
from rest_framework.pagination import PageNumberPagination
from backend.api.google.user import api_google_get_userinfo
from django.conf import settings
import string, random, json
from api.models.user.user_subscription import UserSubscription
from backend.i18n.register_confirm_mail import i18n_get_register_confirm_mail_subject, i18n_get_register_activate_mail_subject
from lss.views.custom_jwt import CustomTokenObtainPairSerializer
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from backend.api.facebook.page import api_fb_get_page_business_profile
from backend.api.instagram.profile import api_ig_get_profile_info
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User as AuthUser
import pytz, stripe
from backend.python_rq.python_rq import email_queue
from business_policy.subscription_plan import SubscriptionPlan
from service.email.email_service import EmailService

from django.http import HttpResponse
import xlsxwriter
from backend.pymongo.mongodb import db
from dateutil.relativedelta import relativedelta
from backend.i18n.email.subject import i18n_get_reset_password_mail_subject
from django.core.exceptions import FieldError

import hashlib
import service

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

#-----------------------------------------admin----------------------------------------------------------------------------------------------

    @action(detail=False, methods=['POST'], url_path=r'admin/create/(?P<role>[^/.]+)', permission_classes=(IsAdminUser,))
    @api_error_handler
    def admin_create_user(self, request, role):
        name, email, activated_country, months = getdata(request, ("name", "email", "activated_country", "months"), required=True)
        contact_number, timezone, plan  = getdata(request, ("contact_number", "timezone","plan"), required=False)
        
        AdminCreateAccountRuleChecker.check(
            **{'role':role ,'email':email, 'activated_country':activated_country, 'months':months, 'contact_number':plan, 'timezone': timezone}
        )

        now = datetime.now(pytz.timezone(timezone)) if timezone in pytz.common_timezones else datetime.now()
        expired_at = now+timedelta(days=30*months) 
        password = ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8))

        auth_user = AuthUser.objects.create_user(
            username=name, email=email, password=password)
        
        user_subscription = UserSubscription.objects.create(
            name=name, 
            status='new', 
            expired_at=expired_at, 
            user_plan= {"activated_platform" : ["facebook","youtube","instagram"]}, 
            meta_country={ 'activated_country': activated_country },
            type='dealer' if role=='dealer' else plan,
            )
        
        User.objects.create(
            name=name, 
            email=email, 
            type='user', 
            status='valid', 
            timezone=timezone if timezone != "" else "Asia/Singapore",
            phone=contact_number, 
            auth_user=auth_user, 
            user_subscription=user_subscription
        )
        
        ret = {
            "name":name,
            "email":email,
            "pass":password,
            "activated_country":activated_country, 
            "plan":plan,
            "expired_at":expired_at.strftime("%d %B %Y %H:%M"),
        }

        return Response(ret, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'search_list', permission_classes=(IsAdminUser,))
    @api_error_handler
    def search_api_user(self, request):
        try:
            search_column = request.query_params.get('search_column')
            keyword = request.query_params.get('keyword')
            print(search_column)
            print(keyword)
            kwargs = {}
            if (search_column in ["", None]) and (keyword not in [None, ""]):
                raise ApiVerifyError("search_column field can not be empty when keyword has value")
            if (search_column not in ['undefined', '']) and (keyword not in ['undefined', '', None]):
                kwargs = { search_column + '__icontains': keyword }

            queryset = User.objects.all().order_by('id').filter(**kwargs)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.dat

            return Response(data, status=status.HTTP_200_OK)
        except FieldError:
            return Response({"error": f"Cannot resolve search_column '{search_column}'"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'admin/activate_seller', permission_classes=(IsAdminUser,))
    @api_error_handler
    def admin_activate_seller(self, request):

        seller_id, activated_country, months = getdata(request, ("seller_id", "activated_country", "months"), required=True)
        seller_queryset = User.objects.filter(id=seller_id, type="user")
        
        if len(seller_queryset) == 0:
            raise ApiVerifyError("no seller found.")
        elif len(seller_queryset) == 1:
            seller_object = seller_queryset[0]
        else:
            raise ApiVerifyError("multiple seller found.")
        
        if seller_object.status == "valid":
            raise ApiVerifyError("The seller has been activated.")
        contact_number, timezone, plan  = getdata(request, ("contact_number", "timezone","plan"), required=False)
        
        AdminCreateAccountRuleChecker.check(
            **{'role': "seller" , 'activated_country':activated_country, 'months':months, 'contact_number':plan, 'timezone': timezone}
        )

        now = datetime.now(pytz.timezone(timezone)) if timezone in pytz.common_timezones else datetime.now()
        expired_at = now+timedelta(days=30*months) 
        password = ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8))
        
        user_subscription = UserSubscription.objects.create(
            name=seller_object.name,
            status='new', 
            expired_at=expired_at, 
            user_plan= {"activated_platform" : ["facebook","youtube","instagram"]}, 
            meta_country={ 'activated_country': activated_country },
            type=plan,
            remark=seller_object.email
        )
        api_user, created = User.objects.update_or_create(pk=seller_id, defaults={
            "status": "valid",
            "timezone": timezone if timezone != "" else "Asia/Singapore",
            "phone": contact_number if contact_number != "" else None,
            "user_subscription": user_subscription
        })
        
        auth_user = api_user.auth_user
        auth_user.set_password(password)
        auth_user.save()
        
        ret = {
            "name":api_user.name,
            "email":api_user.email,
            "pass":password,
            "activated_country":activated_country, 
            "plan":plan,
            "expired_at":expired_at.strftime("%d %B %Y %H:%M"),
        }

        return Response(ret, status=status.HTTP_200_OK)


#-----------------------------------------dealer----------------------------------------------------------------------------------------------

    @action(detail=False, methods=['POST'], url_path=r'dealer/create', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def dealer_create_user(self, request):

        api_user = Verify.get_seller_user(request)
        dealer_user_subscription = Verify.get_dealer_user_subscription_from_api_user(api_user)

        name, email, plan, months, activated_country = getdata(request, ("name", "email", "plan", "months", "activated_country"), required=True)
        contact_number, timezone  = getdata(request, ("contact_number", "timezone"), required=False)
        
        DealerCreateAccountRuleChecker.check(
            **{'dealer_user_subscription':dealer_user_subscription, 'email':email, 'activated_country':activated_country, 'months':months, 'contact_number':plan}
        )
        now = datetime.now(pytz.timezone(timezone)) if timezone in pytz.common_timezones else datetime.now()
        expired_at = now+timedelta(days=30*months) 
        password = ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8))

        auth_user = AuthUser.objects.create_user(
            username=f'{name}', email=email, password=password)
        
        user_subscription = UserSubscription.objects.create(
            name=f'{name}', 
            status='new', 
            expired_at=expired_at, 
            user_plan= {"activated_platform" : ["facebook","youtube","instagram"]}, 
            meta_country={ 'activated_country': activated_country },
            type=plan,
            dealer = dealer_user_subscription)
        
        User.objects.create(
            name=f'{name}', email=email, type='user', status='valid', phone=contact_number, auth_user=auth_user, user_subscription=user_subscription)
        
        #TODO subtract dealer lincense

        ret = {
            "name":f'{name}',
            "email":email,
            "pass":password,
            "activated_country":activated_country, 
            "plan":plan,
            "expired_at":expired_at.strftime("%d %B %Y %H:%M"),
        }

        return Response(ret, status=status.HTTP_200_OK)


#-----------------------------------------buyer----------------------------------------------------------------------------------------------


    #facebook
    @action(detail=False, methods=['POST'], url_path=r'customer_login')
    @api_error_handler
    def customer_login(self, request, pk=None):
        return facebook_login_helper(request, user_type='customer')

    

    
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
        
    @action(detail=False, methods=['GET'], url_path=r'google_customer_login_callback')
    @api_error_handler
    def google_customer_login_callback(self, request):
        return google_login_helper(request, user_type='customer')


#-----------------------------------------seller----------------------------------------------------------------------------------------------
    #facebook
    @action(detail=False, methods=['POST'], url_path=r'user_login')
    @api_error_handler
    def user_login(self, request, pk=None):
        return facebook_login_helper(request, user_type='user')

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


    
    @action(detail=False, methods=['POST'], url_path=r'create/valid_api_user', permission_classes=(IsAdminUser,))
    # @action(detail=False, methods=['POST'], url_path=r'create/valid_api_user', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def create_valid_api_user(self, request):
        name, email = getdata(request, ("name","email"), required=True)
        email = email.lower()
        # print(name,email)
        if User.objects.filter(email=email, type='user').exists():
            api_user = User.objects.get(email=email, type='user')
            api_user.status='valid'
            api_user.save()
        else:
            User.objects.create(name=name, email=email, type='user', status='valid')

        return Response("ok", status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'register/hubspot/webhook', permission_classes=())
    @api_error_handler
    def handle_new_registeration_from_hubspot(self, request):

        http_uri = f'{settings.GCP_API_LOADBALANCER_URL}/api/user/register/hubspot/webhook/'
        Verify.is_hubspot_signature_valid(request,'POST',http_uri)

        #TODO

        first_name = ""
        email = ""
        password = ""
        country = ""
        plan = ""
        
        service.sendinblue.transaction_email.RegistraionConfirmationEmail(first_name, email, password, to=email, cc="", country=country).send()
        service.sendinblue.transaction_email.AccountActivationEmail(first_name,plan, email, password, to=email, cc="", country=country).send()

        return Response("ok", status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'register/trial/(?P<country_code>[^/.]+)', permission_classes=())
    @api_error_handler
    def register_free_trial(self, request, country_code):

        
        email, plan = getdata(request, ("email", "plan"), required=True)
        email = email.lower()
        email = email.replace(" ", "")

        firstName, lastName, contactNumber, password, country, timezone = getdata(request, ("firstName", "lastName", "contactNumber", "password", "country", "timezone"), required=False)

        country_plan = SubscriptionPlan.get_country(country_code)

        if plan != 'trial':
            raise ApiVerifyError('plan option error')

        if AuthUser.objects.filter(email = email).exists() or User.objects.filter(email=email, type='user').exists():
            raise ApiVerifyError('This email address has already been registered.')

        now = datetime.now(pytz.timezone(timezone)) if timezone in pytz.common_timezones else datetime.now()
        expired_at = now+timedelta(days=30)

        auth_user = AuthUser.objects.create_user(
            username=f'{firstName} {lastName}', email=email, password=password)
        
        user_subscription = UserSubscription.objects.create(
            name=f'{firstName} {lastName}', 
            status='valid', 
            expired_at=expired_at, 
            user_plan= {"activated_platform" : ["facebook"]}, 
            meta_country={ 'activated_country': [country_code] },
            type='trial',
            lang=country_plan.language
            )
        
        User.objects.create(name=f'{firstName} {lastName}', email=email, type='user', status='valid', phone=contactNumber, auth_user=auth_user, user_subscription=user_subscription)
        
        ret = {
            "Customer Name":f'{firstName} {lastName}', 
            "Email":email,
            "Password":password[:4]+"*"*(len(password)-4),
            "Target Country":country,
            "Your Plan":"Free Trial",
            "Subscription End Date":expired_at.strftime("%d %B %Y %H:%M"),
        }

        EmailService.send_email_template(
            i18n_get_register_confirm_mail_subject(country_plan.language),
            email,
            "register_confirmation.html",
            {
                'firstName': firstName,
                'email': email,
                'password': password
            },lang=country_plan.language
        )

        EmailService.send_email_template(
            i18n_get_register_activate_mail_subject(country_plan.language),
            email,
            "register_activation.html",
            {
                'firstName': firstName,
                'Plan': plan,
                'email': email,
                'password': password
            },lang=country_plan.language
        )
      
        lss_email = 'hello@liveshowseller.ph' if country_code =='PH' else 'lss@algotech.app'

        subject = "New LSS User - " + firstName + ' ' + lastName + ' - ' + plan
        EmailService.send_email_template(subject,lss_email,"register_cc.html",{
                'firstName': firstName,
                'lastName': lastName,
                'plan': plan,
                'phone': contactNumber,
                'email': email,
                'password': password,
                'expired_at': expired_at.strftime("%d %B %Y %H:%M"),
                'country': country
            })

        return Response(ret, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'register/validate/(?P<country_code>[^/.]+)', permission_classes=())
    @api_error_handler
    def validate_register_data(self, request, country_code):

        # STRIPE_API_KEY = "sk_test_51J2aFmF3j9D00CA0KABMZVKtOVnZNbBvM2hcokicJmfx8vvrmNyys5atEAcpp0Au2O3HtX0jz176my7g0ozbinof00RL4QAZrY" #TODO put it in settings
        STRIPE_API_KEY = "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" #TODO put it in settings
        
        email, plan, period = getdata(request, ("email", "plan", "period"), required=True)
        email = email.lower()
        email = email.replace(" ", "") #TODO add in checkrule

        promoCode, = getdata(request, ("promoCode",), required=False)

        country_plan = SubscriptionPlan.get_country(country_code)
        subscription_plan = country_plan.get_plan(plan)

        if promoCode and promoCode != country_plan.promo_code:
            raise ApiVerifyError('invalid promo code')

        if AuthUser.objects.filter(email=email).exists() or User.objects.filter(email=email, type='user').exists():
            raise ApiVerifyError('This email address has already been registered.')
        
        amount = subscription_plan.get('price',{}).get(period)
        if not amount :
            raise ApiVerifyError('invalid period')

        if promoCode == country_plan.promo_code:
            amount = amount*country_plan.promo_discount_rate
    
        stripe.api_key = STRIPE_API_KEY  
        try:
            intent = stripe.PaymentIntent.create( amount=int(amount*100), currency=country_plan.currency, receipt_email = email)
        except Exception:
            raise ApiCallerError("invalid email")

        return Response({
            "client_secret":intent.client_secret,
            "payment_amount":amount,
            "user_plan":plan
        }, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'register/(?P<country_code>[^/.]+)', permission_classes=())
    @api_error_handler
    def user_register(self, request, country_code):

       
        # STRIPE_API_KEY = "sk_test_51J2aFmF3j9D00CA0KABMZVKtOVnZNbBvM2hcokicJmfx8vvrmNyys5atEAcpp0Au2O3HtX0jz176my7g0ozbinof00RL4QAZrY" #TODO put it in settings
        STRIPE_API_KEY = "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" #TODO put it in settings

        email, password, plan, period, intentSecret = getdata(request,("email", "password", "plan", "period", "intentSecret"),required=True)
        email = email.lower()
        email = email.replace(" ", "")

        firstName, lastName, contactNumber, country , promoCode, timezone = getdata(request, ("firstName", "lastName", "contactNumber", "country", "promoCode", "timezone"), required=False)

        payment_intent_id = intentSecret[:27]
        stripe.api_key = STRIPE_API_KEY
        paymentIntent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if paymentIntent.status != "succeeded":
            raise ApiVerifyError('payment not succeeded')

        #last validation  (require refunds)
        # ------------------------------------------------------------------------------------

        country_plan = SubscriptionPlan.get_country(country_code)
        subscription_plan = country_plan.get_plan(plan)

        if AuthUser.objects.filter(email = email).exists() or User.objects.filter(email=email, type='user').exists():
            raise ApiVerifyError('This email address has already been registered.')

        amount = subscription_plan.get('price',{}).get(period)

        if not amount :
            raise ApiVerifyError('invalid period')

        if promoCode and promoCode != country_plan.promo_code:
            raise ApiVerifyError('invalid promo code')

        if promoCode :
            amount = amount*country_plan.promo_discount_rate

        if int(amount*100) != paymentIntent.amount:
            raise ApiVerifyError('payment amount error')
        #------------------------------------------------------------------------------------

        now = datetime.now(pytz.timezone(timezone)) if timezone in pytz.common_timezones else datetime.now()
        expired_at = now+timedelta(days=30) if period == "monthly" else now+timedelta(days=60)
        
        auth_user = AuthUser.objects.create_user(
            username=f'{firstName} {lastName}', email=email, password=password)
        
        user_subscription = UserSubscription.objects.create(
            name=f'{firstName} {lastName}', 
            status='valid', 
            expired_at=expired_at, 
            user_plan= {"activated_platform" : ["facebook","youtube","instagram"]}, 
            meta_country={ 'activated_country': [country_code] },
            meta = {"stripe payment intent":intentSecret},
            type=plan,
            lang=country_plan.language)
        
        User.objects.create(
            name=f'{firstName} {lastName}', email=email, type='user', status='valid', phone=contactNumber, auth_user=auth_user, user_subscription=user_subscription)
        
        ret = {
            "Customer Name":f'{firstName} {lastName}',
            "Email":email,
            "Password":password[:4]+"*"*(len(password)-4),
            "Target Country":country, 
            "Your Plan":subscription_plan.get('text'),
            "Subscription Period":"Monthly",
            "Subscription End Date":expired_at.strftime("%d %B %Y %H:%M"),
            "Receipt":paymentIntent.charges.get('data')[0].get('receipt_url')
        }

        EmailService.send_email_template(i18n_get_register_confirm_mail_subject(lang=country_plan.language),email,"register_confirmation.html",{
                    'firstName': firstName,
                    'email': email,
                    'password': password
                },lang=country_plan.language)

        EmailService.send_email_template(i18n_get_register_activate_mail_subject(lang=country_plan.language),email,"register_activation.html",{
                    'firstName': firstName,
                    'Plan': subscription_plan.get('text'),
                    'email': email,
                    'password': password
                },lang=country_plan.language)
        
        lss_email = 'lss@algotech.app'
        if country_code == 'PH':
            lss_email = 'hello@liveshowseller.ph'

        subject = "New LSS User - " + firstName + ' ' + lastName + ' - ' + plan
        EmailService.send_email_template(subject,lss_email,"register_cc.html",{
                    'firstName': firstName,
                    'lastName': lastName,
                    'plan': subscription_plan.get('text'),
                    'phone': contactNumber,
                    'email': email,
                    'password': password,
                    'expired_at': expired_at.strftime("%d %B %Y %H:%M"),
                    'country': country
                })

        return Response(ret, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'login/general')
    @api_error_handler
    def general_login(self, request):
        email, password = getdata(request, ("email","password"), required=True)
        
        if not AuthUser.objects.filter(email=email).exists():
            return Response({"message": "email or password incorrect"}, status=status.HTTP_401_UNAUTHORIZED)

        auth_user = AuthUser.objects.get(email=email)

        if not auth_user.check_password(password):
            return Response({"message": "email or password incorrect"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = CustomTokenObtainPairSerializer.get_token(auth_user)

        ret = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(ret, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'seller/account', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_user_account_info(self, request):

        api_user = Verify.get_seller_user(request)
        return Response(UserSerializerAccountInfo(api_user).data, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['GET'], url_path=r'report', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def get_member_grown_report(self, request): 
        title_map = {
            'user_subscription_id': 'Subscription Id',
            'name': 'Name',
            'email': 'Email',
            'phone': 'Phone',
            'country': 'Country',
            'plan': 'Plan',
            'created_at': 'Created at',
            
        }   
        column_list = ['user_subscription_id', 'name', 'email', 'phone', 'country', 'plan', 'created_at']
        datenow = datetime.now().strftime('%Y-%m')
        startdate = datetime(datetime.now().year, datetime.now().month, 1)
        enddate = startdate + relativedelta(months=1)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=LSS_Member_Growing_' + datenow + '.xlsx'

        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        header = workbook.add_format({
            'bold': True,
            'bg_color': '#F7F7F7',
            'color': 'black',
            'align': 'center',
            'valign': 'top',
            'border': 1
        })
        int_center = workbook.add_format({
            'align': 'center'
        })

        row, column = 1, 0
        for column_title in column_list:
            worksheet.write(row, column, title_map[column_title], header)
            if len(column_title) >= 8:
                worksheet.set_column(row, column, len(title_map[column_title]) + 2)
            column += 1
        row += 1
        column = 0

        users = db.api_user.find({'created_at': {'$gte': startdate, '$lte': enddate}, 'type': 'user', 'status': 'valid'})
        for user in users:
            subscription_id = int(user.get('user_subscription_id', 1))
            print (user['id'])
            print (subscription_id)
            for column_title in column_list:
                col_data = user.get(column_title, '')
                if column_title == 'created_at':
                    col_data = col_data.strftime("%Y-%m-%d")
                    worksheet.write(row, column, col_data)
                elif column_title == 'country':
                    country = db.api_user_subscription.find_one({'id': subscription_id}).get('meta_country', {}).get('country', '')
                    worksheet.write(row, column, country)
                elif column_title == 'plan':
                    plan = db.api_user_subscription.find_one({'id': subscription_id}).get('type', '')
                    worksheet.write(row, column, plan)
                else:
                    if type(col_data) == int or type(col_data) == float:
                        worksheet.write(row, column, col_data, int_center)
                    else:
                        worksheet.write(row, column, col_data)
                column += 1
            column = 0
            row += 1

        workbook.close()

        return response


    @action(detail=False, methods=['POST'], url_path=r'password/change', permission_classes=(IsAuthenticated))
    @api_error_handler
    def change_password(self, request):

        password, new_password = getdata(request, ("password","new_password"), required=True)

        auth_user = request.user

        if not auth_user.check_password(password):
            return Response({"message": "password incorrect"}, status=status.HTTP_401_UNAUTHORIZED)

        SellerChangePasswordRuleChecker.check(**{"password":password,"new_password":new_password})

        auth_user.set_password(new_password)
        auth_user.save()

        return Response({"message":"complete"}, status=status.HTTP_200_OK)

    

    @action(detail=False, methods=['POST'], url_path=r'password/forgot')
    @api_error_handler
    def forget_password(self, request):

        email, = getdata(request, ("email",), required=True)
        email = email.lower()
        email = email.replace(" ", "")

        if not AuthUser.objects.filter(email=email).exists() or not User.objects.filter(email=email,type='user').exists():
            raise ApiVerifyError('The account doesn’t exist')

        auth_user = AuthUser.objects.get(email=email)
        api_user = User.objects.get(email=email,type='user')
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        code = PasswordResetCodeManager.generate(auth_user.id,user_subscription.lang)

        EmailService.send_email_template(
            i18n_get_reset_password_mail_subject(user_subscription.lang),
            email,
            "email_reset_password_link.html",
            {"url":settings.GCP_API_LOADBALANCER_URL +"/lss/#/password/reset","code":code,"username":auth_user.username},
            lang=user_subscription.lang)

        return Response({"message":"The email has been sent"}, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['POST'], url_path=r'password/reset')
    @api_error_handler
    def reset_password(self, request):

        code, new_password = getdata(request, ( "code","new_password"), required=True)

        SellerResetPasswordRuleChecker.check(**{"new_password":new_password})
        ret = PasswordResetCodeManager.execute(code, new_password)
        
        return Response(ret, status=status.HTTP_200_OK)



