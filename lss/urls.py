"""lss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

from lss.views.custom_jwt import (CustomTokenObtainPairView,
                                  CustomTokenRefreshView,
                                  CustomTokenVerifyView)

from backend.views.test_view import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('chat_bot/', include('chat_bot.urls')),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('custom_token/', CustomTokenObtainPairView.as_view(),
         name='custom_token_obtain_pair'),
    path('custom_token/refresh/', CustomTokenRefreshView.as_view(),
         name='custom_token_refresh'),
    path('custom_token/verify/', CustomTokenVerifyView.as_view(),
         name='custom_token_verify'),
    path('backend/', index)
]
