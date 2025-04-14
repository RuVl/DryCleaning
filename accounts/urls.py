from django.urls import path

from . import views

urlpatterns = [
	path('register/', views.register_view, name='register'),
	path('login/', views.login_view, name='login'),
	path('logout/', views.logout_view, name='logout'),
	path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
	path('staff/reports/daily/', views.report_daily, name='report_daily'),
	path('staff/reports/monthly/', views.report_monthly, name='report_monthly'),
	path('staff/reports/yearly/', views.report_yearly, name='report_yearly'),
	path('staff/reports/branch/', views.report_branch, name='report_branch'),
	path('staff/reports/services/', views.report_services, name='report_services'),
]
