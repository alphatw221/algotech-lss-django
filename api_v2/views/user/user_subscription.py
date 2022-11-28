from re import sub
from tracemalloc import start
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from itsdangerous import Serializer
from numpy import require
from django.db.models import Q, Value

from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser

from api import rule, models

import stripe, pytz, lib, service, business_policy, json
from database.lss._config import db

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import database

class UserSubscriptionSerializerName(models.user.user_subscription.UserSubscriptionSerializer):
    class Meta:
        model = models.user.user_subscription.UserSubscription
        fields = ['name','id']

class WalletSerializerWithSellerInfo(models.user.buyer_wallet.BuyerWalletSerializer):
    user_subscription = UserSubscriptionSerializerName(read_only=True, default=dict)
    
class UserSerializerBuyerAccountInfo(models.user.user.UserSerializer):
    wallets = WalletSerializerWithSellerInfo(many=True, read_only=True, default=list)

class OrderSerializerWithBuyerAccountInfo(models.order.order.OrderSerializer):
    buyer = UserSerializerBuyerAccountInfo()

class UserSubscriptionAccountInfo(models.user.user_subscription.UserSubscriptionSerializer):

    facebook_pages = models.facebook.facebook_page.FacebookPageInfoSerializer(
        many=True, read_only=True, default=list)
    instagram_profiles = models.instagram.instagram_profile.InstagramProfileInfoSerializer(
        many=True, read_only=True, default=list)
    youtube_channels = models.youtube.youtube_channel.YoutubeChannelInfoSerializer(
        many=True, read_only=True, default=list)
    twitch_channels = models.twitch.twitch_channel.TwitchChannelInfoSerializer(
        many=True, read_only=True, default=list)
    tiktok_accounts = models.tiktok.tiktok_account.TikTokAccountInfoSerializer(
        many=True, read_only=True, default=list)
    product_categories = models.product.product_category.ProductCategorySerializer(
        many=True, read_only=True, default=list)
class UserSerializerSellerAccountInfo(models.user.user.UserSerializer):
    user_subscription = UserSubscriptionAccountInfo(read_only=True, default=dict)

class UserSubscriptionPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    
    queryset = models.user.user_subscription.UserSubscription.objects.all().order_by('id')
    pagination_class = UserSubscriptionPagination

    @action(detail=False, methods=['PUT'], url_path=r'seller/update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_update_subscription(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        #temp
        language, = lib.util.getter.getdata(request,('lang',))
        api_user.lang = language
        api_user.save()

        # request.data['decimal_places'] = int(request.data['decimal_places'])
        serializer = models.user.user_subscription.UserSubscriptionSerializerUpdate(user_subscription,data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(UserSerializerSellerAccountInfo(api_user).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT'], url_path=r'seller/switch_mode', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_switch_subscription_mode(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        subscripton_status, = lib.util.getter.getdata(request,('status',))
        if subscripton_status not in [models.user.user_subscription.STATUS_TEST, models.user.user_subscription.STATUS_PRODUCTION]:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid_subscription_status')
        serializer = models.user.user_subscription.UserSubscriptionSerializerUpdate(user_subscription, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(UserSerializerSellerAccountInfo(api_user).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'seller/upload/animation', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def upload_animation(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        animation, = lib.util.getter.getdata(request, ("animation", ), required=True)
        if not animation:
            raise lib.error_handle.error.api_error.ApiVerifyError('no_animation')

        animation_name=str(datetime.utcnow().timestamp())+animation.name.replace(" ","")
        animation_path = f'user_subscription/{user_subscription.id}/animations'
        animation_url = lib.util.storage.upload_image(animation_path, animation_name, animation)
        static_asset = models.user.static_assets.StaticAssets.objects.create(user_subscription=user_subscription, name=animation.name, path=animation_url, type=models.user.static_assets.TYPE_ANIMATION)
        data = models.user.static_assets.StaticAssetsSerializer(static_asset).data
        return Response(data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['PUT'], url_path=r'payment/(?P<payment_key>[^/.]+)', parser_classes=(MultiPartParser, JSONParser, FormParser), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_payment(self, request, payment_key):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        if payment_key == 'direct_payment':
            data, = lib.util.getter.getdata(request, ('data',), required=False)
            data = json.loads(data)


            for index, account in enumerate(data.get('v2_accounts')):
                key = account.get('name','')+f'_{index}'
                image=request.data.get(key)
                if image in ['null', None, '', 'undefined']:
                    continue
                elif image =='._no_image':
                    account['image'] = settings.GOOGLE_STORAGE_STATIC_DIR+models.user.user_subscription.IMAGE_NULL
                    continue
                elif image.size > models.user.user_subscription.IMAGE_MAXIMUM_SIZE:
                    continue
                elif image.content_type not in models.user.user_subscription.IMAGE_SUPPORTED_TYPE:
                    continue
                image_name = image.name.replace(" ","")
                image_dir = f'user_subscription/{user_subscription.id}/payment/direct_payment'
                image_url = lib.util.storage.upload_image(image_dir, image_name, image)
                account['image'] = image_url
        else:
            data = request.data

        if type(user_subscription.meta_payment.get(payment_key))==dict:
            user_subscription.meta_payment[payment_key].update(data)
        else:
            user_subscription.meta_payment[payment_key]=data

        user_subscription.save()

        return Response(UserSerializerSellerAccountInfo(api_user).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['PUT'], url_path=r'delivery', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_delivery(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        user_subscription.meta_logistic.update(request.data)
        user_subscription.save()

        return Response(UserSerializerSellerAccountInfo(api_user).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'platform/(?P<platform_name>)/(?P<platform_id>)', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_single_platform_instance(self, request, platform_name, platform_id):

        instance = models.user.user_subscription.PLATFORM_ATTR[platform_name]['model'].objects.get(id=platform_id)
        serializer = models.user.user_subscription.PLATFORM_ATTR[platform_name]['serializer']
        return Response(serializer(data=instance).data, status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['GET'], url_path=r'platform/(?P<platform_name>[^/.]+)', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_platform_instances(self, request, platform_name):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        queryset = getattr(user_subscription, models.user.user_subscription.PLATFORM_ATTR[platform_name]['attr']).all()
        serializer = models.user.user_subscription.PLATFORM_ATTR[platform_name]['serializer']
        return Response(serializer(queryset,many=True).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT'], url_path=r'platform/unbind/all', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def unbind_platform_all(self, request):
        
        unbind_platforms, = lib.util.getter.getdata(request, ('unbind_platforms',), required=True)
        if unbind_platforms in [None, '', "undefined", 'null']:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid_data')
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        for platform_name in unbind_platforms:
            campaigns_connected_to_the_platform = user_subscription.campaigns.exclude(end_at__lte=datetime.utcnow())
            campaigns_connected_to_the_platform.update(**{models.user.user_subscription.PLATFORM_ATTR[platform_name]['attr'][:-1]:None, f'{platform_name}_campaign':{}})
            
            queryset = getattr(user_subscription, models.user.user_subscription.PLATFORM_ATTR[platform_name]['attr']).all()
            queryset.delete()

        return Response({"data": unbind_platforms}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'platform/(?P<platform_name>[^/.]+)/unbind', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def unbind_platform_instance(self, request, platform_name):

        platform_instance_id, = lib.util.getter.getparams(request, ('instance_id',), with_user=False)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        platform_instance = lib.util.verify.Verify.get_platform_from_user_subscription(user_subscription,platform_name,platform_instance_id)

        campaigns_connected_to_the_platform = user_subscription.campaigns.exclude(end_at__lte=datetime.utcnow())
        campaigns_connected_to_the_platform.update(**{models.user.user_subscription.PLATFORM_ATTR[platform_name]['attr'][:-1]:None, f'{platform_name}_campaign':{}})
        
        getattr(user_subscription, models.user.user_subscription.PLATFORM_ATTR[platform_name]['attr']).remove(platform_instance)
        
        if not platform_instance.user_subscriptions.all().exists():
            platform_instance.delete()

        queryset = getattr(user_subscription, models.user.user_subscription.PLATFORM_ATTR[platform_name]['attr']).all()
        serializer = models.user.user_subscription.PLATFORM_ATTR[platform_name]['serializer']
        return Response(serializer(queryset,many=True).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['PUT'], url_path=r'platform/(?P<platform_name>[^/.]+)/bind', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def bind_platform_instances(self, request, platform_name):
        
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        if platform_name == models.user.user_subscription.PLATFORM_FACEBOOK:
            lib.helper.subscription_helper.bind_facebook_pages(request, user_subscription)
        
        elif platform_name == models.user.user_subscription.PLATFORM_INSTAGRAM:
            lib.helper.subscription_helper.bind_instagram_profiles(request, user_subscription)
       
        elif platform_name == models.user.user_subscription.PLATFORM_YOUTUBE:
            lib.helper.subscription_helper.bind_youtube_channels(request, user_subscription) 
        
        elif platform_name == models.user.user_subscription.PLATFORM_TWITCH:
            lib.helper.subscription_helper.bind_twitch_channels(request, user_subscription)
        elif platform_name == models.user.user_subscription.PLATFORM_TIKTOK:
            lib.helper.subscription_helper.bind_tiktok_accounts(request, user_subscription)
                   
        queryset = getattr(user_subscription, models.user.user_subscription.PLATFORM_ATTR[platform_name]['attr']).all()
        serializer = models.user.user_subscription.PLATFORM_ATTR[platform_name]['serializer']
        return Response(serializer(queryset,many=True).data, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['GET'], url_path=r'twitch_channel', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_user_subscription_twitch_channel(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        return Response(models.twitch.twitch_channel.TwitchChannelSerializer(user_subscription.twitch_channels.all(),many=True).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'info/general', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_general_info(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        _json = {

            'currency':user_subscription.currency,
            'buyer_lang':user_subscription.buyer_lang,
            'decimal_places':user_subscription.decimal_places,
            'price_unit':user_subscription.price_unit,
            'delivery_note': user_subscription.meta_logistic.get('delivery_note', ''),
            'special_note' : user_subscription.meta_payment.get('special_note', ''),
            'confirmation_note': user_subscription.meta_payment.get('confirmation_note', ''),
            'meta_point':user_subscription.meta_point,
            "meta_reply":user_subscription.meta_reply,
            "meta_cart_remind":user_subscription.meta_cart_remind
        }
        return Response(_json, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['PUT'], url_path=r'update/info/general', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_general_info(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        currency, buyer_lang, decimal_places, price_unit  =\
                lib.util.getter.getdata(request,('currency', 'buyer_lang', 'decimal_places', 'price_unit'), required=True)
        delivery_note, special_note, confirmation_note, meta_point, meta_reply, meta_cart_remind  =\
                lib.util.getter.getdata(request,('delivery_note', 'special_note', 'confirmation_note', 'meta_point', 'meta_reply', 'meta_cart_remind'), required=False)
        user_subscription.currency=currency
        user_subscription.buyer_lang=buyer_lang
        user_subscription.decimal_places=decimal_places
        user_subscription.price_unit=price_unit
        user_subscription.meta_logistic['delivery_note'] = delivery_note
        user_subscription.meta_payment['special_note'] = special_note
        user_subscription.meta_payment['confirmation_note'] = confirmation_note
        user_subscription.meta_point = meta_point if type(meta_point)==dict else {}
        user_subscription.meta_reply = meta_reply if type(meta_reply)==dict else {}
        user_subscription.meta_cart_remind = meta_cart_remind if type(meta_cart_remind)==dict else {}
        user_subscription.save()

        return Response(UserSerializerSellerAccountInfo(api_user).data, status=status.HTTP_200_OK)
    
        
    @action(detail=False, methods=['POST'], url_path=r'upgrade/intent')
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def upgrade_intent(self, request):
        email, plan, period = lib.util.getter.getdata(request, ("email", "plan", "period"), required=True)
        promoCode, = lib.util.getter.getdata(request, ("promoCode",), required=False)
        api_user = lib.util.verify.Verify.get_seller_user(request)    
        api_user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(api_user_subscription.country)
        subscription_plan = country_plan.get_plan(plan)

        kwargs = {'email':email, 'plan':plan, 'period':period, 'country_plan':country_plan, 'subscription_plan':subscription_plan, 'api_user': api_user, 'api_user_subscription':api_user_subscription, 'promoCode': promoCode}
        kwargs = rule.rule_checker.user_subscription_rule_checker.UpgradeIntentDataRuleChecker.check(**kwargs)

        email = kwargs.get('email')
        amount = kwargs.get('amount')
        adjust_amount = kwargs.get('adjust_amount')
        marketing_plans = kwargs.get('marketing_plans')

        stripe_api_key = settings.STRIPE_API_KEY
        intent = service.stripe.stripe.create_payment_intent(stripe_api_key, amount=int(amount*100), currency=country_plan.currency, receipt_email = email)

        return Response({
            "client_secret":intent.client_secret,
            "payment_amount":amount,
            "user_plan":plan,
            "adjust_amount":adjust_amount,
            "currency": country_plan.currency,
            "marketing_plans": marketing_plans,
            "period":period,
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'upgrade')
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def upgrade(self, request):
        email, password, plan, period, intentSecret, promoCode, timezone = \
            lib.util.getter.getdata(request,("email", "password", "plan", "period", "intentSecret", "promoCode", "timezone"), required=False)
        api_user = lib.util.verify.Verify.get_seller_user(request)    
        api_user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        original_plan = api_user_subscription.type
        payment_intent_id = intentSecret[:27]
        stripe.api_key = settings.STRIPE_API_KEY
        paymentIntent = stripe.PaymentIntent.retrieve(payment_intent_id)

        kwargs = {'paymentIntent':paymentIntent,'email':email,'plan':plan,'period':period, 'promoCode':promoCode, 'api_user_subscription':api_user_subscription, 'api_user': api_user}
        kwargs = rule.rule_checker.user_subscription_rule_checker.UpgradePaymentCompleteChecker.check(**kwargs)

        try:
            country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(api_user_subscription.country)
            subscription_plan = country_plan.get_plan(plan)

            kwargs.update({'country_plan':country_plan, 'subscription_plan':subscription_plan})
            kwargs = rule.rule_checker.user_subscription_rule_checker.UpgradeRequireRefundChecker.check(**kwargs)
        except Exception:
            raise lib.error_handle.error.api_error.ApiVerifyError('data invalid, please contact support team for refunding')

        email = kwargs.get('email')
        amount = kwargs.get('amount')
        adjust_amount = kwargs.get('adjust_amount')

        now = datetime.now(pytz.timezone(timezone)) if timezone in pytz.common_timezones else datetime.now()
        expired_at = now+timedelta(days=90) if period == "quarter" else now+timedelta(days=365)

        data={
                'type': plan,
                'expired_at': expired_at,
                'started_at': now,
                'user_plan': {"activated_platform" : ["facebook","youtube","instagram"]},
                'purchase_price': amount
            }
        data.update(business_policy.subscription_plan.SubscriptionPlan.get_plan_limit(plan))
        serializer = models.user.user_subscription.UserSubscriptionSerializerUpgrade(api_user_subscription, data=data,partial=True)
        if serializer.is_valid():
            api_user_subscription = serializer.save()
            
        serializer = models.user.user_subscription.UserSubscriptionSerializerMeta(
            api_user_subscription, 
            data={
                "meta": {"stripe payment intent":intentSecret}
            },
            partial=True
        )
        if serializer.is_valid():
            api_user_subscription = serializer.save()

        deal_obj = models.user.deal.Deal.objects.create(
                user_subscription=api_user_subscription,
                purchased_plan=plan,
                total=amount,
                payer=api_user,
                original_plan=original_plan,
                status=models.user.deal.STATUS_SUCCESS, 
                payment_time=datetime.utcnow()
            )
        marketing_plans = kwargs.get('marketing_plans')
        for key, val in marketing_plans.items():
            if key == "welcome_gift":
                lib.util.marking_tool.WelcomeGiftUsedMark.mark(api_user, save = True)
                try:
                    promocode_obj = models.user.promotion_code.PromotionCode.objects.get(name=key, api_user=api_user, user_subscription=api_user_subscription)
                    promocode_obj.used_at=datetime.utcnow()
                    promocode_obj.deal = deal_obj
                    promocode_obj.save()
                except:
                    models.user.promotion_code.PromotionCode.objects.create(
                        name=key,
                        api_user=api_user,
                        user_subscription=api_user_subscription,
                        used_at=datetime.utcnow(),
                        deal=deal_obj
                    )
        ret = {
            "Email": email,
            "Your Plan": subscription_plan.get('text'),
            "Subscription Period": period,
            "Subscription End Date": expired_at.strftime("%d %B %Y %H:%M"),
            "Receipt": paymentIntent.charges.get('data')[0].get('receipt_url')
        }
        return Response(ret, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'check_binded_platform', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_binded_platform(self, request):
        def get_current_connected_socail_media(user_subscription):
            platform = []
            if user_subscription.facebook_pages.all().exists():
                platform.append("facebook")
            if user_subscription.instagram_profiles.all().exists():
                platform.append("instagram")
            if user_subscription.youtube_channels.all().exists():
                platform.append("youtube")
            if user_subscription.twitch_channels.all().exists():
                platform.append("twitch")
            if user_subscription.tiktok_accounts.all().exists():
                platform.append("tiktok")
            return platform
        api_user = lib.util.verify.Verify.get_seller_user(request)    
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        # social_meida_connect_limit = globals()[type]['social_meida_connect']
        current_connected_social_media = get_current_connected_socail_media(user_subscription)
        return Response({"binded_platform": current_connected_social_media}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'sales_report', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def report_of_campaigns_in_period(self, request):
        api_user, start_time, end_time = lib.util.getter.getparams(request, ('start_time', 'end_time'), seller=True)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        user_subscription_id = user_subscription.id
        start_time = lib.helper.report_helper.SalesReport.normalize_start_time(start_time)
        end_time = lib.helper.report_helper.SalesReport.normalize_end_time(end_time)
        basic_info = lib.helper.report_helper.SalesReport.get_basic_info(start_time, end_time, user_subscription_id)
        if len(basic_info) == 0:
            raise lib.error_handle.error.api_error.ApiCallerError("No any campaigns in period.")
        top_10_itmes = lib.helper.report_helper.SalesReport.get_top_10_itmes(start_time, end_time, user_subscription_id)
        order_analysis = lib.helper.report_helper.SalesReport.get_order_analysis(start_time, end_time, user_subscription_id)
        report = lib.helper.report_helper.SalesReport.merge_data(basic_info, top_10_itmes, order_analysis)
        return Response(report, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['GET'], url_path=r'list/animation', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_animation(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        static_assets = user_subscription.assets.filter(type=models.user.static_assets.TYPE_ANIMATION)
        
        return Response(models.user.static_assets.StaticAssetsSerializer(static_assets, many=True).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'list/buyers', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyers_list(self, request):
        keyword, page, page_size, = lib.util.getter.getparams(request, ( 'keyword', 'page', 'page_size'),with_user=False)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        buyers = user_subscription.customers.all()
        search_fields = ["name", "email"]
        query = Q()
        if keyword:
            for field in search_fields:
                query |= Q(**{f"{field}__icontains": keyword})
        queryset = buyers.filter(query)
        page = self.paginate_queryset(queryset)
        serializer = UserSerializerBuyerAccountInfo(page, many=True)
        result = self.get_paginated_response(serializer.data)
        data = result.data
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'retrieve/buyers/history', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_buyer_order_history(self, request):
        
        buyer_id, points_relative, page, page_size, = lib.util.getter.getparams(request, ('buyer_id', 'points_relative', 'page', 'page_size'), with_user=False)
        if buyer_id in ["", None,'undefined','null'] or not buyer_id.isnumeric():
            raise lib.error_handle.error.api_error.ApiCallerError("Missing data")
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        buyer = models.user.user.User.objects.get(id=buyer_id)
        queryset = buyer.orders.filter(user_subscription=user_subscription).order_by('-created_at')
        if points_relative == "true":
            queryset=queryset.filter(Q(points_earned__gt = 0)|Q(points_used__gt = 0)|Q(point_discount__gt = 0))
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializerWithBuyerAccountInfo(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            data = OrderSerializerWithBuyerAccountInfo(queryset, many=True).data
        return Response(data, status=status.HTTP_200_OK)
       
# --------------------------------- dealer ---------------------------------
    

    @action(detail=False, methods=['GET'], url_path=r'dashboard/cards', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def dealer_dashboard_cards_analysis(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        dealer_user_subscription = lib.util.verify.Verify.get_dealer_user_subscription_from_api_user(api_user)

        campaigns_analysis = database.lss.dealer.get_dealer_campaigns_info_analysis(dealer_user_subscription.id)

        return Response(campaigns_analysis, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['GET'], url_path=r'dashboard/members/growing', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def dealer_dashboard_members_growing(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        dealer_user_subscription = lib.util.verify.Verify.get_dealer_user_subscription_from_api_user(api_user)
        date_period, = lib.util.getter.getparams(request, ('date_period',), with_user=False)

        subcriptions_count_list = []
        start_date = datetime.now()
        end_date = start_date - relativedelta(years=1) if date_period == 'year' else start_date - relativedelta(months=1)
        while start_date > end_date:
            if date_period == 'year':
                this_end_date = start_date - relativedelta(months=1)
                this_period = f'{this_end_date.year}-{this_end_date.month}'
            elif date_period == 'month':
                this_end_date = start_date - relativedelta(days=1)
                this_period = f'{this_end_date.year}-{this_end_date.month}-{this_end_date.day}'
                
            members_growing = database.lss.dealer.get_dealer_members_growing(dealer_user_subscription.id, start_date, this_end_date)
            count_obj = { this_period: members_growing[0].get('subscription_count') } if members_growing else { this_period: 0 }
            subcriptions_count_list.append(count_obj)
            start_date = this_end_date

        return Response(subcriptions_count_list, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['GET'], url_path=r'dashboard/period/revenue', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def dealer_period_revenue(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        dealer_user_subscription = lib.util.verify.Verify.get_dealer_user_subscription_from_api_user(api_user)
        date_period, country_code = lib.util.getter.getparams(request, ('date_period', 'country_code'), with_user=False)

        dealer_revenue = []
        premium_list = []
        for subscriber in db.api_user_subscription.find({'$and': [{'dealer_id': dealer_user_subscription.id}, {'type': 'premium'}]}):
            premium_list.append(subscriber.get('id'))
        
        start_date = datetime.now()
        if date_period == 'quarter':
            start_date = datetime(start_date.year, 12, 31) 
        end_date = start_date - relativedelta(years=1)
        while start_date > end_date:
            if date_period == 'year':
                this_end_date = start_date - relativedelta(months=1)
                this_period = f'{this_end_date.year}-{this_end_date.month}'
            elif date_period == 'quarter':
                this_end_date = start_date - relativedelta(months=3)
                if this_end_date.month == 12:
                    this_period = 'Q1'
                elif this_end_date.month == 3:
                    this_period = 'Q2'
                elif this_end_date.month == 6:
                    this_period = 'Q3'
                elif this_end_date.month == 9:
                    this_period = 'Q4'

            this_period_revenue = 0
            for premium_id in premium_list: 
                premium_order_count = database.lss.dealer.get_premium_period_order_count(premium_id, start_date, this_end_date)
                if premium_order_count:
                    if country_code == 'MY':
                        this_period_revenue += float(premium_order_count[0].get('order_count', 0) * 0.2)
                    else:
                        this_period_revenue += float(premium_order_count[0].get('order_count', 0) * 0.1)
            
            plan_count = database.lss.dealer.get_dealer_period_revenue(dealer_user_subscription.id, start_date, this_end_date)
            for plan in plan_count:
                if plan.get('_id') == 'trial':
                    continue
                country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(country_code)
                subscription_plan = country_plan.get_plan(plan.get('_id'))
                for period in plan.get('licence_count'):
                    if abs(round(period)) == 1:
                        period_name = 'month'
                    elif abs(round(period)) == 3:
                        period_name = 'quarter'
                    elif abs(round(period)) == 12:
                        period_name = 'year'
                    this_period_revenue += subscription_plan.get('price').get(period_name)
            
            count_obj = { this_period: format(this_period_revenue, '.2f') }
            dealer_revenue.append(count_obj)
            start_date = this_end_date
        
        return Response(dealer_revenue, status=status.HTTP_200_OK)