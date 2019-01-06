from django.shortcuts import render
from .forms import *
# Create your views here.
def req(request):
	context={
	'form':SoldTagForm
	}
	return render(request,"OHWebInterface/submitRenderRequest.html",context)

def dl(request,filename):
	context={}
	response=HTTPResponse()
	response['Content-Disposition']='attachment; filename="%s"'%filename