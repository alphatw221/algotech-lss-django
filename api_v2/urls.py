from django.conf.urls import url, include
from rest_framework import routers

from api_v2.views.product import product


router = routers.DefaultRouter()
router.register(r'product', product.ProductViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]