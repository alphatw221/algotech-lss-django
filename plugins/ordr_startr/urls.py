from django.conf.urls import url, include
from rest_framework import routers


from . import views as ordr_startr_views

router = routers.DefaultRouter()
router.register(r'product', ordr_startr_views.product.ProductViewSet)
router.register(r'cart', ordr_startr_views.cart.CartViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]