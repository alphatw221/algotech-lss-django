from abc import ABC, abstractmethod
from backend.api.facebook.user import api_fb_get_me_accounts
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from api.models.instagram.instagram_profile import InstagramProfile

from api.models.order.order import Order
from api.models.order.pre_order import PreOrder

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


class ApiVerifyError(Exception):
    pass


class VerifyRequestFromWhome(ABC):

    @staticmethod
    @abstractmethod
    def verify(request, pk=None):
        ...










class Verify():

    @staticmethod
    def is_admin(api_user, platform_name, platform):
        try:
            if platform_name == 'facebook':
                status_code, response = api_fb_get_me_accounts(
                    api_user.facebook_info['token'])
                for item in response['data']:
                    if item['id'] == platform.page_id:
                        return True
                return False
            elif platform_name == 'youtube':
                return True
        except Exception as e:
            return False
        return False

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
        if not cls.is_admin(api_user, platform_name, platform):
            raise ApiVerifyError("user is not platform admin")
        return platform
    
    @staticmethod
    def get_pre_order(pre_order_id):
        print(pre_order_id)
        print(type(pre_order_id))
        if not PreOrder.objects.filter(id=pre_order_id).exists():
            raise ApiVerifyError('no pre_order found')
        return PreOrder.objects.get(id=pre_order_id)

    @staticmethod
    def get_user_subscription(platform):
        user_subscriptions = platform.user_subscriptions.all()
        if not user_subscriptions:
            raise ApiVerifyError("platform not in any user_subscription")
        user_subscription = user_subscriptions[0]
        return user_subscription

    @staticmethod
    def get_campaign(platform, campaign_id):
        if not platform.campaigns.filter(id=campaign_id).exists():
            raise ApiVerifyError("no campaign found")
        campaign = platform.campaigns.get(id=campaign_id)
        return campaign

    @staticmethod
    def get_campaign_from_platform(platform, campaign_id):
        if not platform.campaigns.filter(id=campaign_id).exists():
            raise ApiVerifyError("no campaign found")
        campaign = platform.campaigns.get(id=campaign_id)
        return campaign


    @staticmethod
    def get_campaign_product(campaign, campaign_product_id):
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


        class FromSeller(VerifyRequestFromWhome):
            @staticmethod
            def verify(request, pk=None):
                api_user, platform_id, platform_name, campaign_id, campaign_product_id, qty, order_product_id, search= getparams(
                request, ("platform_id", "platform_name", "campaign_id", "campaign_product_id", "qty", "order_product_id", "search"))

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
