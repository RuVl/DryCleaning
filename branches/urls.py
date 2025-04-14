from django.urls import path

from . import views
from .views import BranchListView

urlpatterns = [
	path('branches/', BranchListView.as_view(), name='branches'),
	path('create/', views.branch_create, name='branch_create'),
	path('<int:branch_id>/', views.branch_detail, name='branch_detail'),
	path('<int:branch_id>/edit/', views.branch_edit, name='branch_edit'),
	path('<int:branch_id>/delete/', views.branch_delete, name='branch_delete'),
]
