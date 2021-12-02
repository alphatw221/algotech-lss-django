from django.urls import path

from chat_bot.views.facebook import webhook_facebook

urlpatterns = [
    path('facebook/', webhook_facebook),
]
