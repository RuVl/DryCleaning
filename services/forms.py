from django import forms

from .models import ServiceType


class ServiceTypeForm(forms.ModelForm):
	class Meta:
		model = ServiceType
		fields = ['name', 'category', 'base_price', 'complexity_multiplier', 'urgency_multiplier']
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control'}),
			'category': forms.TextInput(attrs={'class': 'form-control'}),
			'base_price': forms.NumberInput(attrs={'class': 'form-control'}),
			'complexity_multiplier': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '1.0', 'max': '2.0'}),
			'urgency_multiplier': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '1.0', 'max': '2.0'}),
		}
