from django.db import models
from django.db.models.base import Model
from django.contrib.auth.models import User
from django.db.models.fields.related import RelatedField
from django.utils import timezone
# Create your models here.

class Cuenta_func(models.Model):
    cuenta_numero = models.IntegerField()
    def __str__(self):
        return f"Orden #{self.contador} "