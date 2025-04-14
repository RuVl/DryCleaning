from django.contrib import admin

from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
	list_display = ('name', 'address', 'phone', 'opening_hours')
	search_fields = ('name', 'address', 'phone')
