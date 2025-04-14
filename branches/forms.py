from django import forms

from .models import Branch


class BranchForm(forms.ModelForm):
	class Meta:
		model = Branch
		fields = ['name', 'address', 'phone', 'opening_hours']
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control'}),
			'address': forms.TextInput(attrs={'class': 'form-control'}),
			'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}),
			'opening_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Пн-Пт: 9:00-19:00, Сб-Вс: 10:00-17:00'}),
		}
