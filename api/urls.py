from django.urls import include, path
from rest_framework import routers

from api.views.auto_response import auto_response
from api.views.campaign import (campaign, campaign_comment,
                                campaign_lucky_draw, campaign_product)
from api.views.cart import cart_product
from api.views.facebook import facebook_page
from api.views.order import order
from api.views.product import product
from api.views.test import test
from api.views.user import user, user_group, user_plan


def url_setup(urlpatterns):
    router = routers.DefaultRouter()

    router.register(r'test-viewset', test.TestViewSet)
    urlpatterns += [
        path('test/', test.test, name='test'),
        path('test-api/<path>/', test.test_api, name='test_api'),
    ]
    router.register(r'sample', test.SampleViewSet)

    router.register(r'user', user.UserViewSet)
    router.register(r'user-group', user_group.UserGroupViewSet)
    router.register(r'user-plan', user_plan.UserPlanViewSet)

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

    router.register(r'cart-product', cart_product.CartProductViewSet)

    router.register(r'order', order.OrderViewSet)

    urlpatterns.append(path('', include(router.urls)))


urlpatterns = []
url_setup(urlpatterns)
