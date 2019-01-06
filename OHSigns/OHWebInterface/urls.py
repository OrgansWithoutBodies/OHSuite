
from django.urls import path
from .views import * 

urlpatterns = [
    path('request/',req),
    path('',req),
    path('templates/',req),
    path('request/submit',sendreq),
]
