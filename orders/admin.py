from decimal import Decimal

from django.contrib import admin
from django.utils.html import format_html

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'client', 'service_type', 'branch', 'received_at', 'completed_at',
		'urgency_level', 'complexity_level', 'status_colored', 'detailed_status_display', 'assigned_to', 'final_price'
	)
	list_filter = (
		'branch', 'urgency_level', 'complexity_level', 'service_type',
		'status', 'detailed_status', 'assigned_to'
	)
	search_fields = ('client__last_name', 'client__first_name', 'client__patronymic', 'id')
	autocomplete_fields = ['client', 'service_type', 'assigned_to']
	readonly_fields = ['final_price']

	fieldsets = (
		('Клиент и услуга', {
			'fields': ('client', 'service_type', 'branch', 'description')
		}),
		('Параметры заказа', {
			'fields': ('urgency_level', 'complexity_level', 'status', 'detailed_status')
		}),
		('Технолог', {
			'fields': ('assigned_to', 'technician_notes', 'damage_notes', 'recommendations')
		}),
		('Даты', {
			'fields': ('received_at', 'completed_at')
		}),
		('Стоимость', {
			'fields': ('final_price',)
		}),
	)

	def status_colored(self, obj):
		color = {
			'pending': 'gray',
			'in_progress': 'orange',
			'completed': 'green',
			'cancelled': 'red',
		}.get(obj.status, 'black')
		return format_html(f'<b style="color:{color}">{obj.get_status_display()}</b>')

	status_colored.short_description = 'Статус'

	def detailed_status_display(self, obj):
		color_map = {
			'received': '#6c757d',  # gray
			'in_cleaning': '#007bff',  # blue
			'drying': '#17a2b8',  # cyan
			'ironing': '#ffc107',  # yellow
			'quality_check': '#fd7e14',  # orange
			'ready': '#28a745',  # green
			'returned': '#20c997',  # teal
			'cancelled': '#dc3545',  # red
		}
		color = color_map.get(obj.detailed_status, 'black')
		return format_html(f'<b style="color:{color}">{obj.get_detailed_status_display()}</b>')

	detailed_status_display.short_description = 'Детальный статус'

	def save_model(self, request, obj, form, change):
		# Calculate base price
		base_price = obj.service_type.base_price

		# Apply complexity surcharge
		if obj.complexity_level == 'high':
			complexity_surcharge = base_price * Decimal('0.2')  # 20% surcharge
		elif obj.complexity_level == 'medium':
			complexity_surcharge = base_price * Decimal('0.1')  # 10% surcharge
		else:
			complexity_surcharge = Decimal('0')

		# Apply urgency surcharge
		if obj.urgency_level == 'high':
			urgency_surcharge = base_price * Decimal('0.3')  # 30% surcharge
		elif obj.urgency_level == 'medium':
			urgency_surcharge = base_price * Decimal('0.15')  # 15% surcharge
		else:
			urgency_surcharge = Decimal('0')

		# Calculate total price
		total_price = base_price + complexity_surcharge + urgency_surcharge

		# Apply discount for regular customers (3 or more previous orders)
		if obj.client.is_regular:
			discount = total_price * Decimal('0.03')  # 3% discount
			total_price -= discount

		obj.final_price = total_price
		super().save_model(request, obj, form, change)
