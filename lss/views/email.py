
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import translation
from django.conf import settings

def test(request):
    with translation.override('id'):
        return render(request, "email_reset_password_link.html", {"url":settings.GCP_API_LOADBALANCER_URL+"/lss/#/password/reset","username": 'teswt', "code":"123412341234"})
    
