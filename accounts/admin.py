from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'role', 'branch')
	list_filter = ('role', 'branch')
	search_fields = ('user__username', 'user__email')
