from django.contrib import admin
from .models import *
# Register your models here.

class ItemAdmin(admin.ModelAdmin):
    list_display=("nombre","monto_iva", "iva","descripcion","precio")
    search_choices=("nombre","monto_iva", "iva","precio")
    search_fields=("nombre","descripcion")

class ClienteAdmin(admin.ModelAdmin):
    list_display=("nombres","apellidos","correo","usuario_main")
    search_choices=("monto","nombre","apellido")
    search_fields=("nombre", "apellido","correo","usuario_main")

class CuentaAdmin(admin.ModelAdmin):
    list_display=("alias", "local","fecha_hora","subtotal","propina","monto_propina","total","usuario","estado")
    search_choices=("alias", "local","fecha_hora","subtotal","propina","monto_propina","total","usuario","estado")
    search_fields=("alias", "local","usuario","clientes","items")
    list_filter=("fecha_hora","propina","estado")

class LocalAdmin(admin.ModelAdmin):
    list_display=("nombre", "creador","descripcion")
    search_choices=("nombre", "creador")
    search_fields=("nombre", "creador","descripcion")

class ConsumoAdmin(admin.ModelAdmin):
    list_display=("item", "cliente","cuenta","consumo_disparejo","cantidad","monto","monto_iva")
    search_choices=("item", "cliente","cuenta","consumo_disparejo","cantidad","monto","monto_iva")
    search_fields=("item", "cliente")
    list_filter=("consumo_disparejo",)

class SplitAdmin(admin.ModelAdmin):
    list_display=("cuenta", "monto","propina","cliente")
    search_choices=("cuenta", "monto","propina","cliente")
    search_fields=("cuenta","cliente")

admin.site.register(item,ItemAdmin)
admin.site.register(cliente,ClienteAdmin)
admin.site.register(cuenta,CuentaAdmin)
admin.site.register(local,LocalAdmin)
admin.site.register(consumo,ConsumoAdmin)
admin.site.register(split,SplitAdmin)
