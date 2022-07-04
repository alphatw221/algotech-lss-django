from django.conf.urls import url, include
from rest_framework import routers

from api_v2.views.product import product
from api_v2.views.campaign import campaign, campaign_product, campaign_comment
from api_v2.views.user import user, user_subscription
from api_v2.views.order import pre_order, order_product, order
from api_v2.views.facebook import facebook_page
from api_v2.views.youtube import youtube_channel
from api_v2.views.instagram import instagram_profile
from api_v2.views.payment import payment
from api_v2.views.auto_response import auto_response


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
router.register(r'auto-response', auto_response.AutoResponseViewSet)
router.register(r'campaign-comment', campaign_comment.CampaignCommentViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]