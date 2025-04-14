from django.urls import path

from . import views

urlpatterns = [
	path('services/', views.ServiceListView.as_view(), name='service_types'),
	path('prices/', views.PriceListView.as_view(), name='price_list'),
	path('create/', views.service_create, name='service_create'),
	path('<int:service_id>/edit/', views.service_edit, name='service_edit'),
	path('<int:service_id>/delete/', views.service_delete, name='service_delete'),
]
