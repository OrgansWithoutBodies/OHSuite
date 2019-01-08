import os 

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse,FileResponse
# from django.core.servers.basehttp import FileWrapper
from . import OHSoldSigns as signs

# 
def test(request):
	return request
def renderRequest(request,**kw):
	
	print(request)
	print(kw)
	# fn=os.path.join(os.getcwd(),'renderedSigns','temp.pdf')
	f='temp.pdf'
	r=signs.renderSheets(n=(2,6),lw=3,res=100,lblmethod='random',numsheets=2)
	fl,fn=signs.saveSheets(r,fn=f)
	print(fn)

	# response=FileResponse(fl,as_attachment=True,filename='test.pdf')
	response=HttpResponse(open(fl.name,'rb+'),content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="{0}"'.format(fn)
	# response['X-Accel-Redirect'] = fn
	return response
"""
changeable filename
asynchronous waiting/ajax
	spinner while rendering
error handling
"""