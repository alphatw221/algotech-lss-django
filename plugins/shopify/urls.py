from django.conf.urls import url, include
from rest_framework import routers

from . import views as shopify_views

router = routers.DefaultRouter()
router.register(r'cart', shopify_views.cart.CartViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]