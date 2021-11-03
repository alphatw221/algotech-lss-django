from django.urls import path, include
from rest_framework import routers

from .views import (
    auto_response,
    campaign,
    campaign_comment,
    campaign_lucky_draw,
    campaign_order,
    campaign_product,
    order_product,
    order,
    product,
    user,
    test,
)

# def url_setup_test_and_sample(urlpatterns, router):
#     router.register(r'sample', sample.SampleViewSet)
#     urlpatterns += [
#         path('test/', test.test, name='test'),
#         path('test_api/<path>/', test.test_api, name='test_api'),
#     ]
#     router.register(r'test_viewset', test.TestViewSet)


# def url_setup(urlpatterns):
#     """ Init router then set up urlpatterns """
#     router = routers.DefaultRouter()

#     url_setup_test_and_sample(urlpatterns, router)

#     urlpatterns.append(path('', include(router.urls)))


# urlpatterns = []
# url_setup(urlpatterns)


urlpatterns = []
router = routers.DefaultRouter()
#--------------------------------------------------------------------------------------------------------------
router.register(r'test_viewset', test.TestViewSet)
urlpatterns += [
    path('test/', test.test, name='test'),
    path('test_api/<path>/', test.test_api, name='test_api'),
]

router.register(r'auto_response', auto_response.AutoResponseViewSet)

router.register(r'campaign_comment', campaign_comment.CampaignCommentViewSet)
router.register(r'campaign_lucky_draw', campaign_lucky_draw.CampaignLuckyDrawViewSet)
router.register(r'campaign_order', campaign_order.CampaignOrderViewSet)
router.register(r'campaign_product', campaign_product.CampaignProductViewSet)
router.register(r'campaign', campaign.CampaignViewSet)

router.register(r'order_product', order_product.OrderProductViewSet)
router.register(r'order', order.OrderViewSet)

router.register(r'product', product.ProductViewSet)

router.register(r'user', user.UserViewSet)

#--------------------------------------------------------------------------------------------------------------
urlpatterns += router.urls