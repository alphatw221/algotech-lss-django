
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import translation
from django.conf import settings

from django.views.decorators.clickjacking import xframe_options_exempt

@xframe_options_exempt
def iframe_facebook(request):
    print("777")
    return render(request, "iframe_facebook.html", locals())
    
