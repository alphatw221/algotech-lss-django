from django.urls import path, include
from rest_framework import routers

from api.models.user import user_group

from .views import (
    test,
    user,
    user_group,
    auto_response,
    campaign,
    campaign_product,
    campaign_comment,
    campaign_order,
    campaign_lucky_draw,
    product,
    order,
    order_product,
)


def url_setup(urlpatterns):
    router = routers.DefaultRouter()

    router.register(r'test_viewset', test.TestViewSet)
    urlpatterns += [
        path('test/', test.test, name='test'),
        path('test_api/<path>/', test.test_api, name='test_api'),
    ]
    router.register(r'sample', test.SampleViewSet)

    router.register(r'user', user.UserViewSet)
    router.register(r'user_group', user_group.UserGroupViewSet)

    router.register(r'auto_response', auto_response.AutoResponseViewSet)

    router.register(r'campaign_comment',
                    campaign_comment.CampaignCommentViewSet)
    router.register(r'campaign_lucky_draw',
                    campaign_lucky_draw.CampaignLuckyDrawViewSet)
    router.register(r'campaign_order', campaign_order.CampaignOrderViewSet)
    router.register(r'campaign_product',
                    campaign_product.CampaignProductViewSet)
    router.register(r'campaign', campaign.CampaignViewSet)

    # router.register(r'product', product.ProductViewSet)

    # router.register(r'order_product', order_product.OrderProductViewSet)
    # router.register(r'order', order.OrderViewSet)

    urlpatterns.append(path('', include(router.urls)))


urlpatterns = []
url_setup(urlpatterns)
