"""split URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('register', views.register_view, name='register'),
    path('login', views.login_view, name="login"),
    path('home', views.menu_view, name="home"),
    path('about', views.about_view, name="about"),
    path('history', views.history_view, name="history"),
    path('logout', views.logout_user, name="logout"),
    path('add_local',views.add_local,name='add_local'),
    path('remove_local/<int:pk>',views.remove_local,name='remove_local'),
    path('add_friend',views.add_friend,name='add_friend'),
    path('add_item',views.add_item,name='add_item'),
    path('order_item/<int:pk>',views.order_item,name='order_item'),
    path('new_bill/<int:pk>',views.new_bill,name='new_bill'),
    path('edit_friend/<int:pk>',views.edit_friend ,name="edit_friend"),
    path('bill/<int:pk>',views.bill,name='bill'),
    path('delete_order/<int:pk>',views.delete_orden,name='delete_orden'),
]
