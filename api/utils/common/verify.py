from abc import ABC, abstractmethod
from os import stat

from django.conf import settings
from api.models.campaign.campaign import Campaign
from backend.api.facebook.user import api_fb_get_me_accounts
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from api.models.instagram.instagram_profile import InstagramProfile
from api.models.user.user_subscription import UserSubscription

from api.models.order.order import Order
from api.models.order.pre_order import PreOrder

from api.utils.error_handle.error.api_error import ApiVerifyError

def getparams(request, params: tuple, with_user=True, seller=True):
    ret=[]
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

platform_dict = {'facebook':FacebookPage, 'youtube':YoutubeChannel, 'instagram':InstagramProfile}



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
        if not cls.is_platform_admin(api_user, platform_name, platform):
            raise ApiVerifyError("user is not platform admin")
        return platform
    
    @classmethod
    def get_platform_verify_with_token(cls, token, platform_name, platform_id):
        if platform_name not in platform_dict:
            raise ApiVerifyError("no platfrom name found")
        if not platform_dict[platform_name].objects.filter(id=platform_id).exists():
            raise ApiVerifyError("no platfrom found")
        platform =  platform_dict[platform_name].objects.get(
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
        user_subscriptions = api_user.user_subscriptions.all()
        if not user_subscriptions:
            raise ApiVerifyError("user not in any user_subscription")
        user_subscription = user_subscriptions[0]
        return user_subscription

    @staticmethod
    def get_campaign(campaign_id):
        if not Campaign.objects.filter(id=campaign_id).exists():
            raise ApiVerifyError("no campaign found")
        campaign = Campaign.objects.get(id=campaign_id)
        return campaign
    
    @staticmethod
    def get_campaign_from_platform(platform, campaign_id):
        if not platform.campaigns.filter(id=campaign_id).exists():
            raise ApiVerifyError("no campaign found")
        campaign = platform.campaigns.get(id=campaign_id)
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

    class PreOrderApi():

        class FromBuyer(VerifyRequestFromWhome):

            @staticmethod
            def verify(request, pk=None):
                
                api_user, order_product_id, campaign_product_id, qty = getparams(request, ("order_product_id", "campaign_product_id", "qty"), seller=False)
                pre_order=Verify.get_pre_order(pk)
                Verify.user_match_pre_order(api_user, pre_order)

                if order_product_id:
                    order_product = Verify.get_order_product_from_pre_order(pre_order, order_product_id)
                    campaign_product = order_product.campaign_product
                else:
                    order_product=None
                    campaign_product = Verify.get_campaign_product_from_pre_order(pre_order, campaign_product_id) if campaign_product_id else None


                if campaign_product and ( campaign_product.type=='lucky_draw' or campaign_product.type=='lucky_draw-fast'):
                        raise ApiVerifyError("invalid campaign_product")

                return api_user, pre_order, order_product, campaign_product, qty
            
            @staticmethod
            def verify_delivery_info(pre_order):
                verify_message = {}
                check_exist = False
                #TODO 訊息彙整回傳一次
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
                api_user, platform_id, platform_name, campaign_id, campaign_product_id, qty, order_product_id, search= getparams(
                request, ("platform_id", "platform_name", "campaign_id", "campaign_product_id", "qty", "order_product_id", "search"))
                print (api_user)
                Verify.verify_user(api_user)
                platform = Verify.get_platform(api_user, platform_name, platform_id)
                campaign = Verify.get_campaign_from_platform(platform, campaign_id)
                pre_order = Verify.get_pre_order_from_campaign(campaign, pk) if pk else None
                if order_product_id:
                    order_product = Verify.get_order_product_from_pre_order(pre_order, order_product_id)
                    campaign_product = order_product.campaign_product
                else:
                    order_product=None
                    campaign_product = Verify.get_campaign_product_from_pre_order(pre_order, campaign_product_id) if campaign_product_id else None

                return api_user, platform, campaign, pre_order, order_product, campaign_product, qty, search


    
    class OrderApi():

        class FromBuyer(VerifyRequestFromWhome):

            @staticmethod
            def verify(request, pk=None):
                pass

        class FromSeller(VerifyRequestFromWhome):
            @staticmethod
            def verify(request, pk=None):

                params=("platform_name", "platform_id", "campaign_id", "order_id")
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
