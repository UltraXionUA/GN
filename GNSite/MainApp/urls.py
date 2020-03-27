from django.urls import path, include
from .views import helloworld


urlpatterns = [
    path('', helloworld)
]
