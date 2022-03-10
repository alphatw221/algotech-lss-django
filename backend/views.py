from django.contrib.auth import authenticate
from django.shortcuts import redirect, render


def login(request):
    is_superuser = None
    error = None
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None and user.is_superuser:
            return redirect("/backend/dashboard")
        elif user is not None and not user.is_superuser:
            is_superuser = False
        else:
            error = True
    return render(request, "backend/login.html", locals())

def dashboard(request):
    if request.user.is_authenticated:
        return render(request, "backend/dashboard.html", locals())
    return redirect("/backend/login")
    
        
    