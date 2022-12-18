
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import translation
from django.conf import settings

def test(request):
    with translation.override('id'):
        return render(request, "reset_password_link_email.html", {"url":settings.WEB_SERVER_URL+"/lss/#/password/reset","username": 'teswt', "code":"123412341234"})
    
