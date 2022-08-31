from django.conf.urls import url, include
from rest_framework import routers


from . import views as ordr_startr_views

router = routers.DefaultRouter()
router.register(r'product', ordr_startr_views.product.ProductViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]