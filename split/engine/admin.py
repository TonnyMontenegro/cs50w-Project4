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

class OrdenAdmin(admin.ModelAdmin):
    list_display=("item", "cuenta","dividido")
    search_choices=("item", "cuenta","dividido")
    search_fields=("item",)
    list_filter=("dividido",)

class ConsumoAdmin(admin.ModelAdmin):
    list_display=("cliente", "cantidad")
    search_choices=("cliente", "cantidad")
    search_fields=("cliente",)

class SplitAdmin(admin.ModelAdmin):
    list_display=("cuenta", "monto","propina","cliente")
    search_choices=("cuenta", "monto","propina","cliente")
    search_fields=("cuenta","cliente")

admin.site.register(item,ItemAdmin)
admin.site.register(cliente,ClienteAdmin)
admin.site.register(cuenta,CuentaAdmin)
admin.site.register(local,LocalAdmin)
admin.site.register(orden,OrdenAdmin)
admin.site.register(consumo,ConsumoAdmin)
admin.site.register(split,SplitAdmin)
