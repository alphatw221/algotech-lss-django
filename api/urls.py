from django.urls import path, include
from rest_framework import routers
from .views import (
    test
)


def url_setup_test_and_sample(urlpatterns, router):
    pass
    # router.register(r'test_viewset', test.TestViewSet)


def url_setup(urlpatterns):
    """ Init router then set up urlpatterns """
    router = routers.DefaultRouter()

    url_setup_test_and_sample(urlpatterns, router)

    urlpatterns.append(path('', include(router.urls)))


urlpatterns = []
url_setup(urlpatterns)
