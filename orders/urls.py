from django.urls import path

from . import views

urlpatterns = [
	path('create/', views.create_order, name='create_order'),
	path('dashboard/', views.client_dashboard, name='client_dashboard'),
	path('success/', views.order_success, name='order_success'),
	path('all/', views.all_orders, name='all_orders'),
	path('<int:order_id>/', views.order_detail, name='order_detail'),
	path('<int:order_id>/edit/', views.order_edit, name='order_edit'),
	path('<int:order_id>/status/<str:status>/', views.order_set_status, name='order_set_status'),

	# Technician routes
	path('technician/dashboard/', views.technician_dashboard, name='technician_dashboard'),
	path('technician/<int:order_id>/update/', views.order_status_update, name='order_status_update'),
]
