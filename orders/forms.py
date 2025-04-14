from django import forms

from services.models import ServiceType
from .models import Order


class OrderCreateForm(forms.ModelForm):
	class Meta:
		model = Order
		fields = ['service_type', 'urgency_level', 'complexity_level']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['service_type'].queryset = ServiceType.objects.all()


class OrderForm(forms.ModelForm):
	class Meta:
		model = Order
		fields = ['service_type', 'branch', 'urgency_level', 'complexity_level', 'description']
		widgets = {
			'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
			'service_type': forms.Select(attrs={'class': 'form-select'}),
			'branch': forms.Select(attrs={'class': 'form-select'}),
			'urgency_level': forms.Select(attrs={'class': 'form-select'}),
			'complexity_level': forms.Select(attrs={'class': 'form-select'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


# Optional customizations here


class OrderTechnicianForm(forms.ModelForm):
	class Meta:
		model = Order
		fields = ['detailed_status', 'technician_notes', 'damage_notes', 'recommendations']
		widgets = {
			'detailed_status': forms.Select(attrs={'class': 'form-select'}),
			'technician_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Заметки по обработке заказа...'}),
			'damage_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Информация о выявленных повреждениях...'}),
			'recommendations': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Рекомендации по дальнейшему уходу...'}),
		}
