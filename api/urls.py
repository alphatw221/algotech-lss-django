from django.urls import path, include
from rest_framework import routers

from api.views.auto_response.auto_response import AutoResponseViewSet
from api.views.campaign.campaign import CampaignViewSet
from api.views.campaign.campaign_comment import CampaignCommentViewSet
from api.views.campaign.campaign_lucky_draw import CampaignLuckyDrawViewSet
from api.views.campaign.campaign_order import CampaignOrderViewSet
from api.views.campaign.campaign_product import CampaignProductViewSet
from api.views.test.test import SampleViewSet, TestViewSet, test, test_api
from api.views.user.user import UserViewSet
from api.views.user.user_group import UserGroupViewSet
from api.views.user.user_plan import UserPlanViewSet


def url_setup(urlpatterns):
    router = routers.DefaultRouter()

    router.register(r'test_viewset', TestViewSet)
    urlpatterns += [
        path('test/', test, name='test'),
        path('test_api/<path>/', test_api, name='test_api'),
    ]
    router.register(r'sample', SampleViewSet)

    router.register(r'user', UserViewSet)
    router.register(r'user_group', UserGroupViewSet)
    router.register(r'user_plan', UserPlanViewSet)

    router.register(r'auto_response', AutoResponseViewSet)

    router.register(r'campaign_comment', CampaignCommentViewSet)
    router.register(r'campaign_lucky_draw', CampaignLuckyDrawViewSet)
    router.register(r'campaign_order', CampaignOrderViewSet)
    router.register(r'campaign_product', CampaignProductViewSet)
    router.register(r'campaign', CampaignViewSet)

    # router.register(r'product', product.ProductViewSet)

    # router.register(r'order_product', order_product.OrderProductViewSet)
    # router.register(r'order', order.OrderViewSet)

    urlpatterns.append(path('', include(router.urls)))


urlpatterns = []
url_setup(urlpatterns)
