
from django.shortcuts import render
from django.http import HttpResponse

def test(request):

    return render(request, "email_reset_password_link.html", {"url":"https://12341234","username": 'teswt', "code":"123412341234"})
    
