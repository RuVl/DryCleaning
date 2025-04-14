from django.contrib import admin

from .models import ServiceType


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
	list_display = ('name', 'category', 'base_price')
	search_fields = ('name',)
	list_filter = ('category',)
