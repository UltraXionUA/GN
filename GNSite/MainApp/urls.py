from django.urls import path
from . import views
from django.http import HttpRequest

urlpatterns = [
    path('', views.index, name='index'),
    path('update_server/', views.webhook, name='hook')
]

