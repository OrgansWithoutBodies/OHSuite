import os 

from django.shortcuts import render
from django.http import HttpResponse,FileResponse
from . import OHSoldSigns as signs

# 
def test():
	pass
def renderRequest(request,**kw):
	
	print(request)
	print(kw)
	# fn=os.path.join(os.getcwd(),'renderedSigns','temp.pdf')
	fn='temp.pdf'
	r=signs.renderSheets(n=(2,6),lw=3,res=100,lblmethod='random',numsheets=3)
	tmp=signs.saveSheets(r)

	response=FileResponse(tmp,as_attachment=True,filename='testing.pdf')
	# response['Content-Disposition'] = 'attachment; filename="{0}"'.format(fn)
	return response
"""
changeable filename
asynchronous waiting/ajax
	spinner while rendering
error handling
"""