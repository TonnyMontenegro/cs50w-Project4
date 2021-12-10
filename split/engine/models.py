from django.db import models
from django.db.models.base import Model
from django.contrib.auth.models import User
from django.db.models.enums import Choices
from django.db.models.fields.related import RelatedField
from django.utils import timezone
# Create your models here.

class item(models.Model):
    '''modelo de item asociado a local'''
    nombre = models.CharField(max_length=64)                                                            # nombre del item ya sea una bebida alimento o articulo del local, el usuario decide
    descripcion = models.TextField(blank=True, null=True)                                               # una breve descripcion en caso de que el usuario desee detallar mas
    precio = models.DecimalField(decimal_places=2,max_digits=16)                                        # precio del item segun el menu del local
    iva = models.BooleanField(default=True)                                                            # el producto require calcular iva por defecto no,se asume que ya los precios incluyen iva
    monto_iva = models.DecimalField(default=0,decimal_places=2,max_digits=16,blank=True,null=True)      # en caso de que se tenga que calcular iva se almacena aca
    usuario_main = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        verbose_name= "Item"
        verbose_name_plural ="Items"
    def __str__(self):
        return f"{self.pk}: {self.nombre} {self.precio}"

    def IVA(self):
        return self.precio * 0.15

class cliente(models.Model):
    nombres = models.CharField(max_length=64)                                                           # nombres del cliente que acompaña al usuario
    apellidos = models.CharField(max_length=64)                                                         # apellidos del cliente que acompaña al usuario
    correo = models.EmailField(max_length=254,unique=True)                                              # correo electronico al que se enviara el detalle de la cuenta y su consumo personal
    usuario_main =  models.ForeignKey(User,on_delete=models.CASCADE)                                    # usuario que añade a su amigo,para evitar registros duplicados de un mismo usuario
    splits = models.ManyToManyField("cuenta",blank=True,related_name="splits_cliente",through="split")
    class Meta:
        verbose_name= "Cliente"
        verbose_name_plural ="Clientes"
    def __str__(self):
        return f"{self.pk}: {self.nombres} {self.correo} {self.usuario_main}"

    def Main(self):
        return self.usuario_main
    
    def Mail(self):
        return self.correo

class cuenta(models.Model):
    '''este modelo es el que registra la cuenta asociada a un local previamente creado por el usuario'''
    alias = models.CharField(max_length=50)                                                             # Pequeño recordatorio de en cual ocacion fue
    local = models.ForeignKey("local",max_length=50,on_delete=models.CASCADE)                           # nombre del restaurante que visitaremos
    fecha_hora = models.DateTimeField(auto_now_add=True)                                                # fecha y hora de creacion
    subtotal = models.DecimalField(decimal_places=2,max_digits=16,default=0,blank=True)                 # subtotal de cuenta, no incluye iva ni propina
    propina = models.BooleanField(default=True)                                                         # la cuenta paga propina si o no
    monto_propina = models.DecimalField(decimal_places=2,max_digits=16,default=0,blank=True,null=True)  # 10% de propina para el mesero sobre el subtotal
    total = models.DecimalField(decimal_places=2,max_digits=16,default=0,blank=True)                    # total incluyendo propina en caso que haya,iva y todo lo consumido
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)                                          # usuario de split que crea la cuenta
    clientes = models.ManyToManyField(cliente,blank=True,related_name="cliente_cuenta")                 # listado de clientes que acompañan al usuario en la mesa
    items = models.ManyToManyField(item,blank=True,related_name="items_cuenta",through="consumo")       # listado de items que se consumieron
    abierta = "Abierta"
    cerrada = "Cerrada"
    choices=(
        (abierta,"Abierta"),
        (cerrada,"Cerrada")
    )
    estado = models.CharField(max_length=10,choices=choices,default=abierta)                            # Estado de la cuenta si sigue abierta deja añadir mas consumos sino se convierte en un elemento del historial
    class Meta:
        verbose_name= "Cuenta"
        verbose_name_plural ="Cuentas"
    def __str__(self):
        return f"{self.pk}: {self.alias}({self.local}) by {self.usuario} {self.fecha_hora} {self.estado}"

    def Propina(self):
        return self.subtotal * 0.10

    def User(self):
        return self.usuario
    def Total(self):
        return self.total
    def Subtotal(self):
        return self.subtotal
    def Propina(self):
        return self.propina
    def Local(self):
        return self.local

class local(models.Model):
    '''En este modelo un usuario registrara el local para luego asociarle las cuentas e items '''
    nombre = models.CharField(max_length=50)                                # nombre del local
    creador = models.ForeignKey(User,on_delete=models.CASCADE)              # usuario que lo añade a su lista, cada usuario tiene sus propios restaurantes registrados
    descripcion = models.TextField(max_length=512,blank=True,null=True)     # descripcion del local en caso de que el usuario desee detallar mas
    class Meta:
        verbose_name= "Local"
        verbose_name_plural ="Locales"
    def __str__(self):
        return f"{self.pk}: {self.nombre} {self.creador}"

    def Creador(self):
        return self.creador
    def Nombre(self):
        return self.nombre
    
class consumo(models.Model):
    '''modelo que registra los consumos de un usuario'''
    item = models.ForeignKey(item,on_delete=models.CASCADE)                         # item que se esta consumiendo
    cliente = models.ForeignKey(cliente,on_delete=models.CASCADE)                   # cliente que consume el item
    cuenta = models.ForeignKey(cuenta,on_delete=models.CASCADE)                     # cuenta en la que esta asociado el consumo
    consumo_disparejo  = models.BooleanField(default=False)                         # si un producto es de consumo disparejo una persona puede consumir mas que los demas por lo que cada usuario paga lo correspondiente a su consumo
    cantidad = models.IntegerField(default=0)       # cantidad en caso de que sea de consumo disparejo
    monto = models.DecimalField(max_digits=16, decimal_places=2,default=0)          # monto que le corresponde en caso de que sea de consumo parejo sera divdir el precio del item entre los que consumen,en caso contrario seria el consumo multiplicado por el precio
    monto_iva = models.DecimalField(max_digits=16, decimal_places=2,default=0)      # monto que corresponde pagar a este 
    class Meta:
        verbose_name= "Consumo"
        verbose_name_plural ="Consumos"
    def __str__(self):
        return f"{self.pk}: {self.cliente} {self.item} {self.monto} {self.cantidad}"

    def Item(self):
        return self.item
    def Cliente(self):
        return self.cliente

class split(models.Model):
    propina = models.DecimalField(decimal_places=2,max_digits=16,default=0,blank=True,null=True)    # el monto de propina que se debe pagar, la propina se paga entre todos los clientes
    monto = models.DecimalField(decimal_places=2,max_digits=16,default=0,blank=True,null=True)      # monto que debe pagar el usuario en caso de que exista iva ya estara incluido
    cuenta = models.ForeignKey(cuenta,on_delete=models.CASCADE)
    consumos = models.ManyToManyField(consumo,blank=True,related_name="split_consumos")
    cliente = models.ForeignKey(cliente,on_delete=models.CASCADE)
    class Meta:
        verbose_name= "Split"
        verbose_name_plural ="Splits"
    def __str__(self):
        return f"{self.pk}: {self.cliente} {self.monto} {self.cuenta}"

    def Cliente(self):
        return self.cliente
    def Cuenta(self):
        return self.cuenta
    def Monto(self):
        return self.monto
    



class Cuenta_func(models.Model):
    cuenta_numero = models.IntegerField()
    def __str__(self):
        return f"Orden #{self.cuenta_numero} "