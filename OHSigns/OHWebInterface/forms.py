from django import forms
from django.forms import formset_factory

class SoldTagForm(forms.Form):#@todo gets connected to chapter/book parse function
	nx=forms.IntegerField(min_value=1,max_value=4)
	ny=forms.IntegerField(min_value=1,max_value=10)
	lw=forms.IntegerField(min_value=0,max_value=10)
	numsheets=forms.IntegerField(min_value=1,max_value=100)
