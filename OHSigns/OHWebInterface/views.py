from django.shortcuts import render
from .forms import *
from OHSignRenderer import views as renderer
# Create your views here.
def req(request):
	context={
	'form':SoldTagForm
	}

	return render(request,"OHWebInterface/submitRenderRequest.html",context)

def dl(request,filename):
	context={}
	response['Content-Disposition']='attachment; filename="%s"'%filename

def sendreq(request):
	print(request)
	return renderer.renderRequest(request,test=2)