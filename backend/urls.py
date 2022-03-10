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
from backend.views import login, dashboard

urlpatterns = [
    path('login/', login),
    path('dashboard/', dashboard)
    # path('add_subscription/', ),
    # path('accounts/', ),
    # path('transactions/', ),
    # path('licenses/', ),
    # path('licenses_details/', ),
    # path('plans/', ),
    # path('sellers/', ),
    # path('buyers/', ),
    # path('order_history/', ),
    # path('settings/', ),
]
