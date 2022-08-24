from pyexpat import model
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from itsdangerous import Serializer
from numpy import require

from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser


from api import rule
from api import models
from api import utils

import lib
import service
import business_policy

import json
from datetime import datetime
class UserSubscriptionPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = ()
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

        return Response(models.user.user.UserSerializerAccountInfo(api_user).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'seller/upload/animation', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def upload_animation(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        animation, = lib.util.getter.getdata(request, ("animation", ), required=True)
        if animation:
            animation_path = default_storage.save(
                f'{user_subscription.id}/luckydraw/{animation.name}', ContentFile(animation.read()))
            models.user.static_assets.StaticAssets.objects.create(user_subscription=user_subscription, name=animation.name, path=animation_path, type=models.user.static_assets.TYPE_ANIMATION)
        
        return Response({'message': 'success'}, status=status.HTTP_200_OK)


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
                    account['image'] = models.user.user_subscription.IMAGE_NULL
                    continue
                elif image.size > models.user.user_subscription.IMAGE_MAXIMUM_SIZE:
                    continue
                elif image.content_type not in models.user.user_subscription.IMAGE_SUPPORTED_TYPE:
                    continue
                
                image_path = default_storage.save(
                        f'/{user_subscription.id}/payment/direct_payment/{image.name}', ContentFile(image.read()))
                account['image'] = image_path
        else:
            data = request.data

        if type(user_subscription.meta_payment.get(payment_key))==dict:
            user_subscription.meta_payment[payment_key].update(data)
        else:
            user_subscription.meta_payment[payment_key]=data

        user_subscription.save()

        return Response(models.user.user.UserSerializerAccountInfo(api_user).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['PUT'], url_path=r'delivery', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_delivery(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        user_subscription.meta_logistic.update(request.data)
        user_subscription.save()

        return Response(models.user.user.UserSerializerAccountInfo(api_user).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'platform/(?P<platform_name>[^/.]+)', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_platform_instances(self, request, platform_name):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        queryset = getattr(user_subscription, models.user.user_subscription.PLATFORM_ATTR[platform_name]['attr']).all()
        serializer = models.user.user_subscription.PLATFORM_ATTR[platform_name]['serializer']
        return Response(serializer(queryset,many=True).data, status=status.HTTP_200_OK)



    @action(detail=False, methods=['PUT'], url_path=r'platform/(?P<platform_name>[^/.]+)/unbind', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def unbind_platform_instance(self, request, platform_name):

        platform_instance_id, = lib.util.getter.getparams(request, ('instance_id',), with_user=False)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        platform_instance = lib.util.verify.Verify.get_platform_from_user_subscription(user_subscription,platform_name,platform_instance_id)

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
            channel_name, = lib.util.getter.getparams(request, ('channel_name',), with_user=False)
            lib.helper.subscription_helper.bind_twitch_channels(request, user_subscription, channel_name)
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
            'confirmation_note': user_subscription.meta_payment.get('confirmation_note', '')
        }
        return Response(_json, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['PUT'], url_path=r'update/info/general', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_general_info(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        currency, buyer_lang, decimal_places, price_unit  =\
                lib.util.getter.getdata(request,('currency', 'buyer_lang', 'decimal_places', 'price_unit'), required=True)
        delivery_note, special_note, confirmation_note  =\
                lib.util.getter.getdata(request,('delivery_note', 'special_note', 'confirmation_note'), required=False)
        user_subscription.currency=currency
        user_subscription.buyer_lang=buyer_lang
        user_subscription.decimal_places=decimal_places
        user_subscription.price_unit=price_unit
        user_subscription.meta_logistic['delivery_note'] = delivery_note
        user_subscription.meta_payment['special_note'] = special_note
        user_subscription.meta_payment['confirmation_note'] = confirmation_note

        user_subscription.save()

        return Response(models.user.user.UserSerializerAccountInfo(api_user).data, status=status.HTTP_200_OK)
    
        
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


# --------------------------------- admin console ---------------------------------
    
    @action(detail=False, methods=['GET'], url_path=r'dashboard/cards', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def dealer_dashboard_cards_analysis(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        dealer_user_subscription = lib.util.verify.Verify.get_dealer_user_subscription_from_api_user(api_user)

        queryset = dealer_user_subscription.subscribers.all()

        print (queryset)

        return Response({'message': 'suc'}, status=status.HTTP_200_OK)