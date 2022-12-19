import imp
from django.conf.urls import url, include
from rest_framework import routers

from api_v2.views.product import product, product_category
from api_v2.views.campaign import campaign, campaign_product, campaign_comment, campaign_lucky_draw, campaign_quiz_game
from api_v2.views.user import user, user_subscription
from api_v2.views.order import pre_order, order_product, order
from api_v2.views.facebook import facebook_page
from api_v2.views.youtube import youtube_channel
from api_v2.views.instagram import instagram_profile
from api_v2.views.payment import payment
from api_v2.views.delivery import delivery
from api_v2.views.auto_response import auto_response
from api_v2.views.business_policy import business_policy
from api_v2.views.cart import cart
from api_v2.views.discount_code import discount_code
from api_v2.views.twitch import twitch_channel
from api_v2.views.tiktok import tiktok_live

from api_v2.views.webhook import hubspot
router = routers.DefaultRouter()
router.register(r'product', product.ProductViewSet)
router.register(r'product-category', product_category.ProductCatoegoryViewSet)
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
router.register(r'delivery', delivery.DeliveryViewSet)
router.register(r'auto-response', auto_response.AutoResponseViewSet)
router.register(r'campaign-comment', campaign_comment.CampaignCommentViewSet)
router.register(r'campaign-luckydraw', campaign_lucky_draw.CampaignLuckyDrawViewSet)
router.register(r'campaign-quizgame', campaign_quiz_game.CampaignQuizGameViewSet)
router.register(r'business-policy',business_policy.BusinessPolicyViewSet)
router.register(r'cart',cart.CartViewSet)
router.register(r'discount-code',discount_code.DiscountCodeViewSet)
router.register(r'twitch',twitch_channel.TwitchViewSet)
router.register(r'tiktok',tiktok_live.TikTokViewSet)
router.register(r'hubspot', hubspot.HubspotViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
]