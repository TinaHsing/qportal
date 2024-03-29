from django import forms
from django.forms import ModelForm
from .models import software, customer


class uploadFileForm(forms.Form):
	file = forms.FileField()

class createSoftwareForm(ModelForm):
	class Meta:
		model = software
		fields = ['name', 'pc', 'discription', 'history']

	def clean_name(self):
		name = self.cleaned_data.get('name')
		sw = software.objects.filter(name = name)
		if sw.count():
			print("error")
			raise forms.ValidationError('Software already exists')
		return name 

class createCustomerForm(ModelForm):
	class Meta:
		model = customer 
		fields = '__all__'
		widgets ={
			'add': forms.TextInput(attrs={'size':150})
		}

	def clean_name(self):
		name = self.cleaned_data.get('name')
		cu = customer.objects.filter(name = name)
		if cu.count():
			print("error")
			raise forms.ValidationError('Customer already exists')
		return name 
	
class updateCustomerForm(ModelForm):
	class Meta:
		model = customer 
		fields = '__all__'

