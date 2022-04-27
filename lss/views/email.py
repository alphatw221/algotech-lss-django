
from django.shortcuts import render
from django.http import HttpResponse

def index(request):

    return render(request, "email_reset_password_link.html", {"posts": posts})
    
