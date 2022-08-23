from django.conf.urls import url, include
from rest_framework import routers


from . import views as easy_store_views

router = routers.DefaultRouter()
router.register(r'product', easy_store_views.product.ProductViewSet)
router.register(r'cart', easy_store_views.cart.CartViewSet)
router.register(r'order', easy_store_views.order.OrderViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]