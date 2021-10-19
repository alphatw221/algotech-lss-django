from django.urls import path, include
from rest_framework import routers

from api.views import sample
from .views import (
    test,
    sample,
)


def url_setup_test_and_sample(urlpatterns, router):
    router.register(r'sample', sample.SampleViewSet)
    urlpatterns += [
        path('test/', test.test, name='test'),
        path('test_api/<path>/', test.test_api, name='test_api'),
    ]
    router.register(r'test_viewset', test.TestViewSet)


def url_setup(urlpatterns):
    """ Init router then set up urlpatterns """
    router = routers.DefaultRouter()

    url_setup_test_and_sample(urlpatterns, router)

    urlpatterns.append(path('', include(router.urls)))


urlpatterns = []
url_setup(urlpatterns)
