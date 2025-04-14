from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile, UserRole


class UserRegisterForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	role = forms.ChoiceField(choices=UserRole.choices)

	class Meta:
		model = User
		fields = ['username', 'email', 'password']

	def save(self, commit=True):
		user = super().save(commit=False)
		user.set_password(self.cleaned_data['password'])
		if commit:
			user.save()
			profile = UserProfile.objects.get(user=user)
			profile.role = self.cleaned_data['role']
			profile.save()
		return user


class UserCreationForm(BaseUserCreationForm):
	email = forms.EmailField(required=True)
	first_name = forms.CharField(max_length=30, required=True)
	last_name = forms.CharField(max_length=30, required=True)
	patronymic = forms.CharField(max_length=30, required=False)
	phone = forms.CharField(max_length=20, required=True)

	class Meta:
		model = User
		fields = ("username", "email", "first_name", "last_name", "patronymic", "phone", "password1", "password2")

	def save(self, commit=True):
		user = super().save(commit=False)
		user.email = self.cleaned_data["email"]
		user.first_name = self.cleaned_data["first_name"]
		user.last_name = self.cleaned_data["last_name"]
		if commit:
			user.save()
			# Create client profile
			from clients.models import Client
			Client.objects.create(
				user=user,
				first_name=self.cleaned_data["first_name"],
				last_name=self.cleaned_data["last_name"],
				patronymic=self.cleaned_data.get("patronymic", ""),
				phone=self.cleaned_data["phone"],
				email=self.cleaned_data["email"]
			)
		return user
