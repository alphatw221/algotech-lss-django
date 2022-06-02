from abc import ABC, abstractmethod
from os import stat

from django.conf import settings
from api.models.campaign.campaign import Campaign
from backend.api.facebook.page import api_fb_get_page_posts
from backend.api.facebook.user import api_fb_get_me_accounts
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from api.models.instagram.instagram_profile import InstagramProfile
from api.models.user.user_subscription import UserSubscription

from api.models.order.order import Order
from api.models.order.pre_order import PreOrder

from api.utils.error_handle.error.api_error import ApiVerifyError
from backend.api.instagram.profile import api_ig_get_profile_live_media
from backend.api.youtube.channel import api_youtube_get_list_channel_by_token
from business_policy.subscription_plan import SubscriptionPlan
import hashlib

def getparams(request, params: tuple, with_user=True, seller=True):
    ret = []
    if with_user:
        if seller:
            if not request.user.api_users.filter(type='user').exists():
                raise ApiVerifyError('no api_user found')
            ret = [request.user.api_users.get(type='user')]
        else:
            if not request.user.api_users.filter(type='customer').exists():
                raise ApiVerifyError('no api_user found')
            ret = [request.user.api_users.get(type='customer')]
    for param in params:
        ret.append(request.query_params.get(param, None))
    return ret


platform_dict = {'facebook': FacebookPage, 'youtube': YoutubeChannel, 'instagram': InstagramProfile}


class VerifyRequestFromWhome(ABC):

    @staticmethod
    @abstractmethod
    def verify(request, pk=None):
        ...


class Verify():

    @staticmethod
    def is_platform_admin(api_user, platform_name, platform):
        try:
            if platform_name == 'facebook':
                status_code, response = api_fb_get_me_accounts(
                    api_user.facebook_info['token'])

                for item in response['data']:
                    if item['id'] == platform.page_id:
                        return True
                return False
            elif platform_name == 'youtube':
                # return api_user.youtube_info[''] == platform.xxx
                return True
            elif platform_name == 'instagram':
                # api_user.instagram_info['']

                return True
        except Exception as e:
            return False
        return False

    @staticmethod
    def language_supported(language):
        if language not in settings.SUPPORTED_LANGUAGES:
            raise ApiVerifyError('language not supported')

    @staticmethod
    def check_is_admin_by_token(token, platform_name, platform):
        try:
            if platform_name == 'facebook':
                status_code, response = api_fb_get_me_accounts(
                    token)
                for item in response['data']:
                    if item['id'] == platform.page_id:
                        return True
                return False
            elif platform_name == 'youtube':
                # return api_user.youtube_info[''] == platform.xxx
                return True
            elif platform_name == 'instagram':
                # api_user.instagram_info['']

                return True
        except Exception as e:
            return False
        return False

    @staticmethod
    def get_customer_user(request):
        if not request.user.api_users.filter(type='customer').exists():
            raise ApiVerifyError('no api_user found')
        return request.user.api_users.get(type='customer')

    @staticmethod
    def get_seller_user(request):
        if not request.user.api_users.filter(type='user').exists():
            raise ApiVerifyError('no api_user found')
        api_user = request.user.api_users.get(type='user')
        if api_user.status != "valid":
            raise ApiVerifyError("not activated user")
        return api_user

    @staticmethod
    def verify_user(api_user):
        if not api_user:
            raise ApiVerifyError("no user found")
        elif api_user.status != "valid":
            raise ApiVerifyError("not activated user")

    @classmethod
    def get_platform(cls, api_user, platform_name, platform_id):
        if platform_name not in platform_dict:
            raise ApiVerifyError("no platfrom name found")
        if not platform_dict[platform_name].objects.filter(id=platform_id).exists():
            raise ApiVerifyError("no platfrom found")
        platform = platform_dict[platform_name].objects.get(
            id=platform_id)
        # if not cls.is_platform_admin(api_user, platform_name, platform):
        #     raise ApiVerifyError("user is not platform admin")
        return platform

    @classmethod
    def get_platform_from_user_subscription(cls, user_subscription, platform_name, platform_id):
        attr_dict = {'facebook': 'facebook_pages', 'youtube': 'youtube_channels', 'instagram': 'instagram_profiles'}

        if platform_name not in attr_dict:
            raise ApiVerifyError('not support platform')

        if not getattr(user_subscription, attr_dict[platform_name]).filter(id=platform_id).exists():
            raise ApiVerifyError('platform not found')

        return getattr(user_subscription, attr_dict[platform_name]).get(id=platform_id)

    @classmethod
    def get_platform_verify_with_token(cls, token, platform_name, platform_id):
        if platform_name not in platform_dict:
            raise ApiVerifyError("no platfrom name found")
        if not platform_dict[platform_name].objects.filter(id=platform_id).exists():
            raise ApiVerifyError("no platfrom found")
        platform = platform_dict[platform_name].objects.get(
            id=platform_id)
        if not cls.check_is_admin_by_token(token, platform_name, platform):
            raise ApiVerifyError("user is not platform admin")
        return platform

    @staticmethod
    def get_pre_order(pre_order_id):
        if not PreOrder.objects.filter(id=pre_order_id).exists():
            raise ApiVerifyError('no pre_order found')
        return PreOrder.objects.get(id=pre_order_id)

    @staticmethod
    def get_order(order_id):
        if not Order.objects.filter(id=order_id).exists():
            raise ApiVerifyError('no order found')
        return Order.objects.get(id=order_id)

    @staticmethod
    def get_order_by_api_user(api_user, order_id):
        if not api_user.orders.filter(id=order_id).exists():
            raise ApiVerifyError('order not found')
        return api_user.orders.get(id=order_id)

    @staticmethod
    def get_user_subscription(user_subscription_id):
        if not UserSubscription.objects.filter(id=user_subscription_id).exists():
            raise ApiVerifyError("user subscription not found")
        return UserSubscription.objects.get(id=user_subscription_id)

    @staticmethod
    def get_user_subscription_from_platform(platform):
        user_subscriptions = platform.user_subscriptions.all()
        if not user_subscriptions:
            raise ApiVerifyError("platform not in any user_subscription")
        user_subscription = user_subscriptions[0]
        return user_subscription

    @staticmethod
    def get_user_subscription_from_api_user(api_user):
        user_subscription = api_user.user_subscription
        if not user_subscription:
            raise ApiVerifyError("no user_subscription")
        return user_subscription

    @staticmethod
    def get_dealer_user_subscription_from_api_user(api_user):
        user_subscription = api_user.user_subscription
        if not user_subscription:
            raise ApiVerifyError("no user_subscription")
        if user_subscription.type != "dealer":
            raise ApiVerifyError("not dealer")
        return user_subscription

    def get_user_subscription_from_dealer_user_subscription(dealer_user_subscription, user_subscription_id):
        if not dealer_user_subscription.subscribers.filter(id=user_subscription_id).exists():
            raise ApiVerifyError("no user_subscription")
        return dealer_user_subscription.subscribers.get(id=user_subscription_id)

    @staticmethod
    def get_facebook_page_from_user_subscription(user_subscription, facebook_page_id):
        if not user_subscription.facebook_pages.filter(id=facebook_page_id).exists():
            raise ApiVerifyError("facebook page not bound to user_subscription")
        return user_subscription.facebook_pages.get(id=facebook_page_id)

    @staticmethod
    def get_youtube_channel_from_user_subscription(user_subscription, youtube_channel_id):
        if not user_subscription.youtube_channels.filter(id=youtube_channel_id).exists():
            raise ApiVerifyError("youtube channel not bound to user_subscription")
        return user_subscription.youtube_channels.get(id=youtube_channel_id)

    @staticmethod
    def get_instagram_profile_from_user_subscription(user_subscription, instagram_profile_id):
        if not user_subscription.instagram_profiles.filter(id=instagram_profile_id).exists():
            raise ApiVerifyError("instagram profile not bound to user_subscription")
        return user_subscription.instagram_profiles.get(id=instagram_profile_id)

    @staticmethod
    def get_campaign(campaign_id):
        if not Campaign.objects.filter(id=campaign_id).exists():
            raise ApiVerifyError("no campaign found")
        campaign = Campaign.objects.get(id=campaign_id)
        return campaign

    @staticmethod
    def get_campaign_from_order(order):
        if not order.campaign:
            raise ApiVerifyError("no campaign found")
        return order.campaign

    @staticmethod
    def get_campaign_from_pre_order(pre_order):
        if not pre_order.campaign:
            raise ApiVerifyError("no campaign found")
        return pre_order.campaign


    @staticmethod
    def get_campaign_from_platform(platform, campaign_id):
        if not platform.campaigns.filter(id=campaign_id).exists():
            raise ApiVerifyError("no campaign found")
        campaign = platform.campaigns.get(id=campaign_id)
        return campaign

    @staticmethod
    def get_campaign_from_user_subscription(user_subscription, campaign_id):
        if not user_subscription.campaigns.filter(id=campaign_id).exists():
            raise ApiVerifyError("no campaign found")
        campaign = user_subscription.campaigns.get(id=campaign_id)
        return campaign

    @staticmethod
    def get_product_from_user_subscription(user_subscription, product_id):
        if not user_subscription.products.filter(id=product_id).exists():
            raise ApiVerifyError("no product found")
        return user_subscription.products.get(id=product_id)

    @staticmethod
    def get_campaign_product_from_campaign(campaign, campaign_product_id):
        if not campaign.products.filter(id=campaign_product_id).exists():
            raise ApiVerifyError('no campaign product found')
        campaign_product = campaign.products.get(id=campaign_product_id)
        return campaign_product

    @staticmethod
    def get_pre_order_from_campaign(campaign, pre_order_id):
        if not campaign.pre_orders.filter(id=pre_order_id).exists():
            raise ApiVerifyError('no pre_order found')
        return campaign.pre_orders.get(id=pre_order_id)

    @staticmethod
    def get_order_product_from_pre_order(pre_order, order_product_id):
        if not pre_order.order_products.filter(id=order_product_id).exists():
            raise ApiVerifyError("no order_product found")
        return pre_order.order_products.get(id=order_product_id)

    @staticmethod
    def get_campaign_product_from_pre_order(pre_order, campaign_product_id):
        if not pre_order.campaign.products.filter(id=campaign_product_id).exists():
            raise ApiVerifyError("no campaign_product found")
        return pre_order.campaign.products.get(id=campaign_product_id)

    @staticmethod
    def is_valid_country_code_for_user_plan(country_code):
        support_country_code = [cls_attribute.__name__  for cls_attribute in SubscriptionPlan.__dict__.values() if type(cls_attribute)==type] #TODO find a better way to do this
        if country_code not in support_country_code:
            raise ApiVerifyError("country code not valid")
            
    @staticmethod
    def is_valid_country_code(country_code):
        if country_code not in ["SG", "PH", "IN", "ID", "MY", "TW", "CN"]:
            raise ApiVerifyError("country code not valid")


    @staticmethod
    def get_auto_response_from_user_subscription(user_subscription, auto_response_id):

        if not user_subscription.auto_responses.filter(id=auto_response_id).exists():
            raise ApiVerifyError("no auto reply found")
        return user_subscription.auto_responses.get(id=auto_response_id)

    @staticmethod
    def user_match_pre_order(api_user, pre_order):
        pass
        # platform_id = pre_order.get('platform_id')
        # platform_name = pre_order.get('platform')

        # if platform_name == 'facebook':
        #     pass
        #     if pre_order.get('customer_id') != api_user.get('facebook_info',{}).get("id"):
        #         raise ApiVerifyError('error!')
        # elif platform_name == 'youtube':
        #     if pre_order.get('customer_id') != api_user.get('google_info',{}).get("id"):
        #         raise ApiVerifyError('error!')
        #     pass
        # else:
        #     pass

    @staticmethod
    def user_match_order(api_user, order):
        pass
        # platform_name = order.get('platform')

        # if platform_name == 'facebook':
        #     pass
        #     if order.get('customer_id') != api_user.get('facebook_info',{}).get("id"):
        #         raise ApiVerifyError('error!')
        # elif platform_name == 'youtube':
        #     if order.get('customer_id') != api_user.get('google_info',{}).get("id"):
        #         raise ApiVerifyError('error!')
        #     pass
        # else:
        #     pass

    @staticmethod
    def is_hubspot_signature_valid(request):
        
        request_body = request.body.decode('utf-8')
        http_method = request.method
        http_uri = settings.GCP_API_LOADBALANCER_URL+request.get_full_path()
        source_string = settings.HUBSPOT_CLIENT_SECRET + http_method + http_uri + request_body

        if request.META.get('HTTP_X_HUBSPOT_SIGNATURE') != hashlib.sha256(source_string.encode('utf-8')).hexdigest():
            raise ApiVerifyError('signature error')

    @staticmethod
    def check_is_page_token_valid(platform_name, officiall_page_token, officiall_page_id=None):
        try:
            if platform_name == 'facebook':
                status_code, response = api_fb_get_page_posts(page_token=officiall_page_token, page_id=officiall_page_id, limit=1)
                if status_code == 200:
                    return True
                print(response)    #for debug
                return False
            elif platform_name == 'youtube':
                status_code, response = api_youtube_get_list_channel_by_token(access_token=officiall_page_token)
                # print("response", response)
                if status_code == 200:
                    return True
                return False
            elif platform_name == 'instagram':
                status_code, response = api_ig_get_profile_live_media(page_token=officiall_page_token, profile_id=officiall_page_id)
                if status_code == 200:
                    return True
                return False
        except Exception as e:
            return False
        return False
    class PreOrderApi():

        class FromBuyer(VerifyRequestFromWhome):

            @staticmethod
            def verify(request, pk=None):

                api_user, order_product_id, campaign_product_id, qty = getparams(request, (
                "order_product_id", "campaign_product_id", "qty"), seller=False)
                pre_order = Verify.get_pre_order(pk)
                Verify.user_match_pre_order(api_user, pre_order)

                if order_product_id:
                    order_product = Verify.get_order_product_from_pre_order(pre_order, order_product_id)
                    campaign_product = order_product.campaign_product
                else:
                    order_product = None
                    campaign_product = Verify.get_campaign_product_from_pre_order(pre_order,
                                                                                  campaign_product_id) if campaign_product_id else None

                if campaign_product and (
                        campaign_product.type == 'lucky_draw' or campaign_product.type == 'lucky_draw-fast'):
                    raise ApiVerifyError("invalid campaign_product")

                return api_user, pre_order, order_product, campaign_product, qty

            @staticmethod
            def verify_delivery_info(pre_order):
                verify_message = {}
                check_exist = False
                # TODO 訊息彙整回傳一次
                if not pre_order.shipping_first_name:
                    check_exist = True
                    verify_message['shipping_first_name'] = 'not valid'
                if not pre_order.shipping_last_name:
                    check_exist = True
                    verify_message['shipping_last_name'] = 'not valid'
                if not pre_order.shipping_phone:
                    check_exist = True
                    verify_message['shipping_phone'] = 'not valid'
                if not pre_order.shipping_postcode:
                    check_exist = True
                    verify_message['shipping_postcode'] = 'not valid'
                if not pre_order.shipping_region:
                    check_exist = True
                    verify_message['shipping_region'] = 'not valid'
                if not pre_order.shipping_location:
                    check_exist = True
                    verify_message['shipping_location'] = 'not valid'
                if not pre_order.shipping_address_1:
                    check_exist = True
                    verify_message['shipping_address'] = 'not valid'
                if not pre_order.shipping_method:
                    check_exist = True
                    verify_message['shipping_method'] = 'not valid'
                if not pre_order.payment_first_name:
                    check_exist = True
                    verify_message['payment_first_name'] = 'not valid'
                if not pre_order.payment_last_name:
                    check_exist = True
                    verify_message['payment_last_name'] = 'not valid'
                if not pre_order.payment_company:
                    check_exist = True
                    verify_message['payment_company'] = 'not valid'
                if not pre_order.payment_postcode:
                    check_exist = True
                    verify_message['payment_postcode'] = 'not valid'
                if not pre_order.payment_region:
                    check_exist = True
                    verify_message['payment_region'] = 'not valid'
                if not pre_order.payment_location:
                    check_exist = True
                    verify_message['payment_location'] = 'not valid'
                if not pre_order.payment_address_1:
                    check_exist = True
                    verify_message['payment_address'] = 'not valid'
                if check_exist == True:
                    return verify_message
                return verify_message

        class FromSeller(VerifyRequestFromWhome):
            @staticmethod
            def verify(request, pk=None):
                api_user, platform_id, platform_name, campaign_id, campaign_product_id, qty, order_product_id, search = getparams(
                    request, (
                    "platform_id", "platform_name", "campaign_id", "campaign_product_id", "qty", "order_product_id",
                    "search"))

                Verify.verify_user(api_user)
                platform = Verify.get_platform(api_user, platform_name, platform_id)
                campaign = Verify.get_campaign_from_platform(platform, campaign_id)
                pre_order = Verify.get_pre_order_from_campaign(campaign, pk) if pk else None
                if order_product_id:
                    order_product = Verify.get_order_product_from_pre_order(pre_order, order_product_id)
                    campaign_product = order_product.campaign_product
                else:
                    order_product = None
                    campaign_product = Verify.get_campaign_product_from_pre_order(pre_order,
                                                                                  campaign_product_id) if campaign_product_id else None

                return api_user, platform, campaign, pre_order, order_product, campaign_product, qty, search

    class OrderApi():

        class FromBuyer(VerifyRequestFromWhome):

            @staticmethod
            def verify(request, pk=None):
                pass

        class FromSeller(VerifyRequestFromWhome):
            @staticmethod
            def verify(request, pk=None):

                params = ("platform_name", "platform_id", "campaign_id", "order_id")
                api_user, platform_name, platform_id, campaign_id, order_id = getparams(request, params)

                Verify.verify_user(api_user)
                platform = Verify.get_platform(api_user, platform_name, platform_id)
                campaign = Verify.get_campaign_from_platform(platform, campaign_id)

                if order_id:
                    if not Order.objects.get(id=order_id):
                        raise ApiVerifyError('no order found')
                    order = Order.objects.get(id=order_id)
                else:
                    order = None

                return platform, campaign, order
