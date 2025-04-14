from django import forms

from .models import Client


class ClientProfileForm(forms.ModelForm):
	class Meta:
		model = Client
		fields = ['last_name', 'first_name', 'patronymic', 'phone', 'email', 'address']
		widgets = {
			'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7XXXXXXXXXX'}),
			'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.com'}),
			'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
		}
