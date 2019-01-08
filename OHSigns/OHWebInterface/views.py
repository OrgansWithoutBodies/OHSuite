from django.shortcuts import render
from .forms import *
from OHSignRenderer import views as renderer
# Create your views here.
def req(request):
	context={
	'form':SoldTagForm
	}

	return render(request,"OHWebInterface/submitRenderRequest.html",context)

def sendreq(request):
	print(request)
	return renderer.renderRequest(request,test=2)