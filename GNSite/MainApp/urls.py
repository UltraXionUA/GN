from django.urls import path
from . import views
from django.http import request

urlpatterns = [
    path('', views.index, name='index'),
    path('/update_server', views.webhook, kwargs=['POST'])
]

