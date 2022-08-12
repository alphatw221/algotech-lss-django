from django.conf.urls import url, include
from rest_framework import routers


from . import views as easy_store_views

router = routers.DefaultRouter()
router.register(r'product', easy_store_views.product.ProductViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
]