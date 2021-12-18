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
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

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
    usuario = cliente.objects.filter(correo=request.user.email).exists()
    if usuario:
        print("URL menu_view: Usuario ya existe en clientes")
    else:
        cliente.objects.create(usuario_main=request.user,nombres=request.user.first_name,apellidos=request.user.last_name,correo=request.user.email)

    open = cuenta.objects.filter(usuario=request.user,estado="Abierta").exists()
    if open:
        cuentax = cuenta.objects.get(usuario=request.user,estado="Abierta")
        context['open'] = True
        return redirect(f"/bill/{cuentax.pk}")

    context['amigos'] = cliente.objects.filter(usuario_main=request.user).exclude(correo=request.user.email).order_by('nombres')
    context['locales'] = local.objects.filter(creador=request.user).order_by('nombre')
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
    context = {}
    openx = cuenta.objects.filter(usuario=request.user,estado="Abierta").exists()
    if openx:

        context['open'] = True
    return render(request,"about.html",context)

def history_view(request):
    context = {}
    context['cuentas'] = cuenta.objects.filter(usuario=request.user,estado="Cerrada")
    return render(request,"history.html",context)

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required(login_url="")
def add_local(request):
    if request.method == "POST":
        Nombre_local = request.POST.get('nombre_local')
        descripcion_local = request.POST.get('descripcion_local')
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
            amigo.save()
            messages.info(request,"amigo editado con exito")


        return redirect('home')

@login_required(login_url="")
def new_bill(request,pk):
    if request.method == "POST":
        clientes=request.POST.getlist('FriendBox')
        user=cliente.objects.get(correo=request.user.email)
        clientes.append(user.pk)
        alias=request.POST.get('alias')

        locals = local.objects.get(pk=pk)

        cuenta.objects.create(alias=alias,local=locals,usuario=request.user)
        clientex=[]
        for x in range(0,len(clientes)):
            clientex.append(cliente.objects.get(pk=clientes[x]))
        cuenta.objects.filter(usuario=request.user).last().clientes.add(*clientex)
        context={}

        context['clientes'] = clientex
        context['local'] = locals
        return redirect(f"/bill/{pk}" ,context)

@login_required(login_url="")
def bill(request,pk):
    context={}
    open = cuenta.objects.filter(usuario=request.user,estado="Abierta").exists()
    if open:
        cuentax = cuenta.objects.get(usuario=request.user,estado="Abierta")
        context['open'] = True
        context['ordenes'] = orden.objects.filter(cuenta=cuentax).all()
        context['cuenta'] = cuentax
        context['clientes'] = cuentax.clientes.all()
        context['items'] = item.objects.filter(usuario_main=request.user)
        context['splits'] = split.objects.filter(cuenta=cuentax).order_by('cliente')

        obj = orden.objects.filter(cuenta=cuentax).all().aggregate(Sum('subtotal'))
        subtotal= obj['subtotal__sum']
        obj = orden.objects.filter(cuenta=cuentax).all().aggregate(Sum('subtotal_iva'))
        subtotal_iva= obj['subtotal_iva__sum']

        cuentax.subtotal = subtotal
        cuentax.total = subtotal_iva
        if subtotal:
            cuentax.monto_propina = float(subtotal) * 0.10
            cuentax.save()
            cuentax.total_propina = float(cuentax.total) + float(cuentax.monto_propina)
            cuentax.save()
            context['monto_propinap'] = cuentax.monto_propina / cuentax.clientes.count()


    return render(request,"bill.html",context)

@login_required(login_url="")
def add_item(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre_item')
        descripcion = request.POST.get('descripcion_item')
        precio = request.POST.get('precio_item')
        iva = request.POST.get('incluye_iva_item')
        if iva is None:
            precio_iva = float(precio) * 0.15
            item.objects.create(nombre=nombre,descripcion=descripcion,precio=precio,iva=False,monto_iva=precio_iva,usuario_main=request.user)

        else:
            item.objects.create(nombre=nombre,descripcion=descripcion,precio=precio,usuario_main=request.user)


        return redirect('home')

@login_required(login_url="")
def order_item(request,pk):
    if request.method == "POST":
        cuentax = cuenta.objects.filter(usuario=request.user,estado="Abierta").last()
        clienteslist= cuentax.clientes.values("pk")

        for clientei in clienteslist:
            cliente_inst=cliente.objects.get(pk=clientei['pk'])
            split_state = split.objects.filter(cuenta=cuentax,cliente=cliente_inst).exists()
            if split_state:
                print("URL order_item: Split ya existe")
            else:
                split.objects.create(cuenta=cuentax,cliente=cliente_inst)


        itemorder = item.objects.get(pk=pk)
        Consumo = request.POST.get('Consumo_individual',"compartida")
        if Consumo == "individual":
            orden.objects.create(item=itemorder,cuenta=cuentax)
            ordenx = orden.objects.filter(item=itemorder,cuenta=cuentax).last()
            numbers=request.POST.getlist('num')
            clientesInsert = []
            for clientei in clienteslist:
                clientesInsert.append(cliente.objects.get(pk=clientei['pk']))
            for x in range(0,len(numbers)):
                if int(numbers[x])>0:
                    splitx = split.objects.get(cuenta=cuentax,cliente=clientesInsert[x])
                    monto = float(itemorder.precio) * float(numbers[x])
                    monto_iva = float(monto) + (float(itemorder.monto_iva)*float(numbers[x]))
                    consumo.objects.create(cliente=clientesInsert[x],cantidad=numbers[x],orden=ordenx,split=splitx,monto=monto,monto_iva=monto_iva)
                    splitx.monto = float(splitx.monto)+((float(itemorder.precio) + float(itemorder.monto_iva))*float(numbers[x]))
                    splitx.save()
            numbers_int = [int(i) for i in numbers]
            ordenx.subtotal = sum(numbers_int)*float(itemorder.precio)
            ordenx.cantidad_total = sum(numbers_int)
            if itemorder.iva == False:
                ordenx.subtotal_iva = (float(ordenx.subtotal)*0.15)+float(ordenx.subtotal)
            else:
                 ordenx.subtotal_iva = ordenx.subtotal
            ordenx.save()

        else:
            num = request.POST.get('num_divided','1')
            orden.objects.create(item=itemorder,cuenta=cuentax,dividido=True,cantidad_total=int(num))
            subtotal=float(num)*(float(itemorder.precio))

            if itemorder.iva == False:
                subtotal_iva = (subtotal*0.15)+subtotal
            else:
                subtotal_iva = subtotal

            ordenx = orden.objects.filter(item=itemorder,cuenta=cuentax).last()
            ordenx.subtotal=subtotal
            ordenx.subtotal_iva=subtotal_iva
            ordenx.save()
            numbers=request.POST.getlist('check')
            splited = float(ordenx.subtotal_iva) / float(len(numbers))
            montop = subtotal / float(len(numbers))
            monto_ivap = subtotal_iva / float(len(numbers))
            for x in range(0,len(numbers)):
                clienteinst = cliente.objects.get(pk=numbers[x])
                splitx = split.objects.get(cuenta=cuentax,cliente=clienteinst)
                consumo.objects.create(cliente=clienteinst,orden=ordenx,split=splitx,monto=montop,monto_iva=monto_ivap)
                splitx.monto = float(splitx.monto)+float(splited)
                splitx.save()

        return redirect(f'/bill/{ordenx.pk}')

@login_required(login_url="")
def delete_orden(request,pk):
    if request.method == "POST":
        Exist = orden.objects.exists()
        if Exist:
            ordenx = orden.objects.get(pk=pk)
            if ordenx.dividido == True:
                splited = float(ordenx.subtotal_iva) / float(consumo.objects.filter(orden=ordenx).count())
                consumosx = consumo.objects.filter(orden=ordenx).all()
                for x in consumosx:
                    splitinst = split.objects.get(pk=x.split.pk)
                    splitinst.monto = float(splitinst.monto) - splited
                    print(f"URL: order_delete: Cantidad total #{ordenx.cantidad_total}")
                    splitinst.save()
            else:
                consumosx = consumo.objects.filter(orden=ordenx).all()
                itemorder= ordenx.item
                for x in consumosx:
                    splited = float(x.cantidad) * (float(itemorder.precio) + float(itemorder.monto_iva))
                    splitinst = split.objects.get(pk=x.split.pk)
                    splitinst.monto = float(splitinst.monto) - splited
                    print(f"URL: order_delete: Cantidad total #{ordenx.cantidad_total}")
                    splitinst.save()

            orden.objects.filter(pk=pk).delete()
            messages.info(request,"Orden removida de su factura")
        else:
            messages.error(request,"Error, la orden no existe")
    return redirect('home')

@login_required(login_url="")
def order_detail(request,pk):
    context={}
    context['orden'] = orden.objects.get(pk=pk)
    context['consumos'] = consumo.objects.filter(orden=context['orden'])
    context['cuenta'] = cuenta.objects.get(pk=context['orden'].cuenta.pk)
    context['splits'] = split.objects.filter(cuenta=context['cuenta'])
    if context['cuenta'].estado == "Abierta":
        context['open'] = True
    else:
        context['open'] = False
    return render(request,"order_detail.html",context)

@login_required(login_url="")
def remove_bill(request,pk):
    cuentainst =cuenta.objects.get(pk=pk)
    cuentainst.clientes.clear()
    cuentainst.ordenes.clear()
    cuentainst.delete()
    messages.info(request,"Cuenta eliminada con exito")
    return redirect('home')

@login_required(login_url="")
def client_detail(request,pk):
    context={}
    context['split'] = split.objects.get(pk=pk)
    context['cuenta'] = cuenta.objects.get(pk=context['split'].cuenta.pk)
    context['consumos'] = consumo.objects.filter(split=context['split'] ,cliente=context['split'] .cliente)
    if context['cuenta'].estado == "Abierta":
        context['open'] = True
    else:
        context['open'] = False
    return render(request,"client_detail.html",context)

@login_required(login_url="")
def generate_bills(request,pk):
    if request.method == "POST":
        propina=request.POST.get('incluye_propina','NO')
        cuentax = cuenta.objects.get(pk=pk)
        splits = split.objects.filter(cuenta=cuentax)
        if propina == "SI":
            prop = cuentax.monto_propina / cuentax.clientes.count()
            context={}
            cuentax.propina = True
            cuentax.save()
            context['cuenta']=cuentax
            context['splits']=splits
            context['ordenes']=orden.objects.filter(cuenta=cuentax)
            for splitx in splits:
                splitx.monto_propina = prop
                splitx.save()

            for splitx in splits:
                context['splitx']= splitx
                context['consumos']= consumo.objects.filter(split=splitx)

                msg_plain = render_to_string('email.txt', context)
                msg_html = render_to_string('email.html',context)

                send_mail(
                    f'Factura de Split orden #047{pk}S',
                    msg_plain,
                    settings.EMAIL_HOST_USER,
                    [splitx.cliente.correo],
                    html_message=msg_html,
                )
        else:
            context={}
            context['cuenta']=cuentax
            context['splits']=splits
            context['ordenes']=orden.objects.filter(cuenta=cuentax)

            cuentax.propina = False
            cuentax.save()

            for splitx in splits:
                context['splitx']= splitx
                context['consumos']= consumo.objects.filter(split=splitx)

                msg_plain = render_to_string('email.txt', context)
                msg_html = render_to_string('email.html',context)

                send_mail(
                    f'Factura de Split orden #047{pk}S',
                    msg_plain,
                    settings.EMAIL_HOST_USER,
                    [splitx.cliente.correo],
                    html_message=msg_html,
                )
    cuentax.estado="Cerrada"
    cuentax.save()
    return redirect("home")


@login_required(login_url="")
def view_bill(request,pk):
    context={}
    cuentax = cuenta.objects.get(pk=pk)
    if cuentax.estado == "Abierta":
        context['open'] = True
    else:
        context['open'] = False
    context['ordenes'] = orden.objects.filter(cuenta=cuentax).all()
    context['cuenta'] = cuentax
    context['clientes'] = cuentax.clientes.all()
    context['items'] = item.objects.filter(usuario_main=request.user)
    context['splits'] = split.objects.filter(cuenta=cuentax).order_by('cliente')

    obj = orden.objects.filter(cuenta=cuentax).all().aggregate(Sum('subtotal'))
    subtotal= obj['subtotal__sum']
    obj = orden.objects.filter(cuenta=cuentax).all().aggregate(Sum('subtotal_iva'))
    subtotal_iva= obj['subtotal_iva__sum']

    cuentax.subtotal = subtotal
    cuentax.total = subtotal_iva
    if subtotal:
        cuentax.monto_propina = float(subtotal) * 0.10
        cuentax.save()
        cuentax.total_propina = float(cuentax.total) + float(cuentax.monto_propina)
        cuentax.save()
        context['monto_propinap'] = cuentax.monto_propina / cuentax.clientes.count()

    return render(request,"view_bill.html",context)
