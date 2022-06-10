from django.conf.urls import url, include
from rest_framework import routers

from api_v2.views.product import product
from api_v2.views.campaign import campaign
from api_v2.views.campaign import campaign_product
from api_v2.views.user import user
from api_v2.views.order import pre_order
from api_v2.views.order import order_product
from api_v2.views.order import order

router = routers.DefaultRouter()
router.register(r'product', product.ProductViewSet)
router.register(r'campaign',campaign.CampaignViewSet)
router.register(r'campaign-product',campaign_product.CampaignProductViewSet)
router.register(r'user', user.UserViewSet)
router.register(r'pre_order', pre_order.PreOrderViewSet)
router.register(r'order-product', order_product.OrderProductViewSet)
router.register(r'order', order.OrderViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]