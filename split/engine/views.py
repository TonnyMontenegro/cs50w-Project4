from django.urls import reverse
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from .models import *
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
    superuser=User.objects.create_user("Admin","Admin@Split.com","Password")
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
    context={}
    context['amigos'] = cliente.objects.filter(usuario_main=request.user)
    context['locales'] = local.objects.filter(creador=request.user)
    return render(request,'menu.html',context)

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

def about_view(request):
    return render(request,"about.html")

def history_view(request):
    return render(request,"history.html")

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required(login_url="")
def add_local(request):
    if request.method == "POST":
        Nombre_local = request.POST.get('nombre_local')
        descripcion_local = request.POST.get('descripcion_local')
        print(Nombre_local)
        existe = local.objects.filter(creador=request.user,nombre=Nombre_local).exists()
        
        if existe:
            messages.error(request,"Ese local ya se encuentra registrado")
        else:
            messages.info(request,"Local registrado con exito")
            local.objects.create(creador=request.user,nombre=Nombre_local,descripcion=descripcion_local)
        
        return redirect('home')

@login_required(login_url="")
def remove_local(request,pk):
    if request.method == "POST":

        local.objects.get(pk=pk).delete()
        messages.info(request,"Local eliminado con exito")
        return redirect('home')

@login_required(login_url="")
def add_friend(request):
    if request.method == "POST":
        nombres = request.POST.get('nombres_friend')
        apellidos = request.POST.get('apellidos_friend')
        correo = request.POST.get('email_friend')

        existe = cliente.objects.filter(usuario_main=request.user,correo=correo).exists()
        
        if existe:
            messages.error(request,"Ese correo ya se encuentra registrado para otro usuario")
        else:
            messages.info(request,"amigo registrado con exito")
            cliente.objects.create(usuario_main=request.user,nombres=nombres,apellidos=apellidos,correo=correo)
        
        return redirect('home')

@login_required(login_url="")
def new_bill(request,pk):
    if request.method == "POST":
        return redirect('home')

@login_required(login_url="")
def edit_friend(request,pk):
    if request.method == "POST":
        nombres = request.POST.get('nombres_friend_edit')
        apellidos = request.POST.get('apellidos_friend_edit')
        correo = request.POST.get('email_friend_edit')

        amigo = cliente.objects.get(pk=pk)
        existe = cliente.objects.filter(correo=correo).exclude(pk=pk).exists()
        
        if existe:
            messages.error(request,"Ese correo ya se encuentra registrado para otro usuario")
        else:
            amigo.nombres = nombres
            amigo.apellidos = apellidos
            amigo.correo = correo
            amigo.save
            messages.info(request,"amigo editado con exito")
            
        
        return redirect('home')