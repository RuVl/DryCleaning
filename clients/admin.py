from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
	list_display = ('last_name', 'first_name', 'patronymic', 'is_regular_display', 'orders_count')
	search_fields = ('last_name', 'first_name', 'patronymic')

	def is_regular_display(self, obj):
		return obj.orders.count() >= 3

	is_regular_display.short_description = 'Постоянный клиент'
	is_regular_display.boolean = True  # галочка/крестик

	def orders_count(self, obj):
		return obj.orders.count()

	orders_count.short_description = 'Количество заказов'
