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
from django.urls import include, path, re_path
from lss.views.iframe import iframe_facebook
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

from lss.views.custom_jwt import (CustomTokenObtainPairView,
                                  CustomTokenRefreshView,
                                  CustomTokenVerifyView)
from django.views.generic import TemplateView

from lss.views.email import test
from lss.views.chat import index,room
from api_v2.views.facebook.facebook import facebook_messenger_webhook
from api_v2.views.oauth.oauth import oauth_redirect
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/v2/', include('api_v2.urls')),
    # path('chat_bot/', include('chat_bot.urls')),
    

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('custom_token/', CustomTokenObtainPairView.as_view(),
         name='custom_token_obtain_pair'),
    path('custom_token/refresh/', CustomTokenRefreshView.as_view(),
         name='custom_token_refresh'),
    path('custom_token/verify/', CustomTokenVerifyView.as_view(),
         name='custom_token_verify'),

    
    path('temp/chat_bot/facebook/', facebook_messenger_webhook),
    path('oauth/redirect/',oauth_redirect),
    
    re_path(r'^lss/',TemplateView.as_view(template_name="lss_entry.html")),
    re_path(r'^seller/',TemplateView.as_view(template_name="lss_enigma_entry.html")),
    re_path(r'^buyer/',TemplateView.as_view(template_name="lss_enigma_entry.html")),
    re_path(r'^admin/',TemplateView.as_view(template_name="lss_enigma_entry.html")),

    path('test',TemplateView.as_view(template_name="reset_password_link_email.html")),
    path('test2',TemplateView.as_view(template_name="reset_password_success_email.html")),
    path('test3',TemplateView.as_view(template_name="facebook_login_example.html")),
    path('iframe/facebook', iframe_facebook),


    #-------------------------plugin---------------------------------------------------
    path('api/plugin/easy_store/', include(('plugins.easy_store.urls','easy_store'), namespace='easy_store')),
    path('api/plugin/ordr_startr/', include(('plugins.ordr_startr.urls','ordr_startr'), namespace='ordr_startr')),
    path('api/plugin/shopify/', include(('plugins.shopify.urls','shopify'), namespace='shopify'))
]
