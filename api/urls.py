
from django.urls import path, include
from rest_framework import routers

from api.views.test import test

from api.views.user import user
from api.views.user import user_group
from api.views.user import user_plan
from api.views.user import user_subscription

from api.views.auto_response import auto_response

from api.views.campaign import campaign
from api.views.campaign import campaign_comment
from api.views.campaign import campaign_lucky_draw
from api.views.campaign import campaign_product

from api.views.facebook import facebook_page

from api.views.product import product


from api.views.order import order
from api.views.order import pre_order
from api.views.dashboard import dashboard
from api.views.payment import payment


from api.views.payment import payment
from api.views.youtube import youtube_channel
from django.views.decorators.csrf import csrf_exempt


def url_setup(urlpatterns):
    router = routers.DefaultRouter()

    router.register(r'test-viewset', test.TestViewSet)
    urlpatterns += [
        path('test/', test.test, name='test'),
        path('test-api/<path>/', test.test_api, name='test_api'),
        path('test_error/', test.test_error, name='test_error'),
    ]
    router.register(r'sample', test.SampleViewSet)

    router.register(r'user', user.UserViewSet)
    router.register(r'user-group', user_group.UserGroupViewSet)
    router.register(r'user-plan', user_plan.UserPlanViewSet)
    router.register(r'user-subscription',
                    user_subscription.UserSubscriptionViewSet)

    router.register(r'auto_response', auto_response.AutoResponseViewSet)

    router.register(r'campaign-comment',
                    campaign_comment.CampaignCommentViewSet)
    router.register(r'campaign-lucky_draw',
                    campaign_lucky_draw.CampaignLuckyDrawViewSet)
    router.register(r'campaign-product',
                    campaign_product.CampaignProductViewSet)
    router.register(r'campaign', campaign.CampaignViewSet)

    router.register(r'facebook_page', facebook_page.FacebookPageViewSet)

    router.register(r'product', product.ProductViewSet)

    router.register(r'order', order.OrderViewSet)

    router.register(r'pre_order', pre_order.PreOrderViewSet)

    router.register(r'dashboard', dashboard.DashboardViewSet)

    router.register(r'payment', payment.PaymentViewSet)

    router.register(r'youtube', youtube_channel.YoutubeViewSet)
    

    urlpatterns.append(path('', include(router.urls)))


urlpatterns = []
url_setup(urlpatterns)
