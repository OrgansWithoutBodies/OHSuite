from django.views.generic.base import RedirectView
from django.urls import path
from .views import * 

urlpatterns = [
    path('',RedirectView.as_view(url='request/')),
    path('request/',req,name='req'),
    path('templates/',req),
    path('request/submit',sendreq),
]
