from types import ClassMethodDescriptorType
from django import forms
from  django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import fields
from django.forms.widgets import PasswordInput,TextInput,TextInput

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(label='Nombre', widget=forms.TextInput(attrs={'class':'form-control',"placeholder":"John"}))
    last_name = forms.CharField(label='Apellidos', widget=forms.TextInput(attrs={'class':'form-control',"placeholder":"Doe"}))
    username = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'class':'form-control',"placeholder":"John_Doe"}))
    email = forms.CharField(label='correo electronico',widget=forms.TextInput(attrs={'class':'form-control',"placeholder":"John@mail.com"}))
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class':'form-control',"placeholder":"S3cuReP4ss_235"}))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class':'form-control',"placeholder":"S3cuReP4ss_235"}))

    class Meta:
        model = User
        fields = ('username','password1','password2','email','first_name','last_name')
        help_text = {k:"" for k in fields }