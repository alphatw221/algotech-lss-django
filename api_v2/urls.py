from django.conf.urls import url, include
from rest_framework import routers

from api_v2.views.product import product
from api_v2.views.campaign import campaign
from api_v2.views.campaign import campaign_product
from api_v2.views.user import user
from api_v2.views.user import user_subscription
from api_v2.views.order import pre_order
from api_v2.views.order import order_product
from api_v2.views.order import order
from api_v2.views.facebook import facebook_page
from api_v2.views.youtube import youtube_channel
from api_v2.views.instagram import instagram_profile
from api_v2.views.payment import payment

router = routers.DefaultRouter()
router.register(r'product', product.ProductViewSet)
router.register(r'campaign',campaign.CampaignViewSet)
router.register(r'campaign-product',campaign_product.CampaignProductViewSet)
router.register(r'user', user.UserViewSet)
router.register(r'user-subscription', user_subscription.UserSubscriptionViewSet)
router.register(r'pre_order', pre_order.PreOrderViewSet)
router.register(r'order-product', order_product.OrderProductViewSet)
router.register(r'order', order.OrderViewSet)
router.register(r'facebook-page', facebook_page.FacebookPageViewSet)
router.register(r'youtube-channel', youtube_channel.YoutubeChannelViewSet)
router.register(r'instagram-profile', instagram_profile.InstagramProfileViewSet)
router.register(r'payment', payment.PaymentViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]