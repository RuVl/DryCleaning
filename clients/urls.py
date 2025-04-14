from django.urls import path

from .views import create_client_profile

urlpatterns = [
	path('create/', create_client_profile, name='create_client_profile'),
]
