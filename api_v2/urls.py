from django.conf.urls import url, include
from rest_framework import routers

from api_v2.views.product import product
from api_v2.views.campaign import campaign
from api_v2.views.user import user


router = routers.DefaultRouter()
router.register(r'product', product.ProductViewSet)
router.register(r'campaign',campaign.CampaignViewSet)
router.register(r'user', user.UserViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]