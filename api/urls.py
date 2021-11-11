from django.urls import path, include
from rest_framework import routers

from api.models.user import user_group

from api.views.test import test

from api.views.user import user
from api.views.user import user_group
from api.views.user import user_plan

from api.views.auto_response import auto_response

from api.views.campaign import campaign
from api.views.campaign import campaign_comment
from api.views.campaign import campaign_lucky_draw
from api.views.campaign import campaign_order
from api.views.campaign import campaign_product


from api.views.facebook import facebook_page

from api.views.product import order_product
from api.views.product import product

from api.views.order import order


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
    router.register(r'user_plan', user_plan.UserPlanViewSet)

    router.register(r'auto_response', auto_response.AutoResponseViewSet)

    router.register(r'campaign_comment',
                    campaign_comment.CampaignCommentViewSet)
    router.register(r'campaign_lucky_draw',
                    campaign_lucky_draw.CampaignLuckyDrawViewSet)
    router.register(r'campaign_order', campaign_order.CampaignOrderViewSet)
    router.register(r'campaign_product',
                    campaign_product.CampaignProductViewSet)
    router.register(r'campaign', campaign.CampaignViewSet)

    router.register(r'facebook_page', facebook_page.FacebookPageViewSet)

    router.register(r'product', product.ProductViewSet)
    router.register(r'order_product', order_product.OrderProductViewSet)

    router.register(r'order', order.OrderViewSet)

    urlpatterns.append(path('', include(router.urls)))


urlpatterns = []
url_setup(urlpatterns)
