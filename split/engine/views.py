from django.urls import reverse
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from .models import Cuenta_func
from django.http import HttpResponse,HttpResponseRedirect, request
from .forms import UserRegisterForm
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.views.defaults import page_not_found

# Create your views here.

contador = Cuenta_func.objects.first()
#creacion de el objeto user con super usuario
superuser = User.objects.filter(is_superuser=True)
if contador is None:
    n_contador =Cuenta_func(cuenta_numero=1)
    n_contador.save()
if superuser.count() == 0:
    superuser=User.objects.create_user("Admin","Admin@pizzapp.com","Password")
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.save()

def index(request):
    if not request.user.is_authenticated:
        return redirect("register")
    else: return redirect("home")

@csrf_protect
def register_view(request):
    if not request.user.is_authenticated:
        form = UserRegisterForm()
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                form.save()
                user= form.cleaned_data.get('username')
                messages.success(request,'Cuenta registrada bajo el nombre de usuario de: '+ user)
                return redirect('login')
        context= {'form':form}
        return render(request, 'register.html',context)
    else: return redirect("home")

@login_required(login_url="login")
def menu_view(request):
    return render(request,'menu.html')

@csrf_protect
def login_view(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username,password=password)

            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                messages.info(request, 'Nombre de usuario o contraseña incorrecta')
        context = {}
        return render(request,"login.html",context)
    else: return redirect("home")

def logout_user(request):
    logout(request)
    return redirect('login')

# def index(request):
#     return HttpResponse("nyaa")