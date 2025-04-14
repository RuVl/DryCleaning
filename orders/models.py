from django.db import models
from django.utils import timezone

from branches.models import Branch
from clients.models import Client
from services.models import ServiceType


class UrgencyLevel(models.TextChoices):
	NORMAL = 'normal', 'Обычная'
	URGENT = 'urgent', 'Срочная'
	EXPRESS = 'express', 'Экспресс'


class ComplexityLevel(models.TextChoices):
	SIMPLE = 'simple', 'Простая'
	MEDIUM = 'medium', 'Средняя'
	COMPLEX = 'complex', 'Сложная'


class OrderStatus(models.TextChoices):
	RECEIVED = 'received', 'Принят'
	IN_CLEANING = 'in_cleaning', 'В чистке'
	DRYING = 'drying', 'Сушка'
	IRONING = 'ironing', 'Глажка'
	QUALITY_CHECK = 'quality_check', 'Контроль качества'
	READY = 'ready', 'Готов'
	RETURNED = 'returned', 'Выдан'
	CANCELLED = 'cancelled', 'Отменен'


class Order(models.Model):
	STATUS_CHOICES = [
		('pending', 'Ожидает'),
		('in_progress', 'В работе'),
		('completed', 'Выполнен'),
		('cancelled', 'Отменен'),
	]

	URGENCY_LEVELS = [
		('low', 'Обычная'),
		('medium', 'Повышенная'),
		('high', 'Срочная'),
	]

	COMPLEXITY_LEVELS = [
		('low', 'Обычная'),
		('medium', 'Средняя'),
		('high', 'Сложная'),
	]

	client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders', verbose_name='Клиент')
	service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT, verbose_name='Тип услуги')
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='orders', verbose_name='Филиал')
	received_at = models.DateTimeField(default=timezone.now, verbose_name='Дата приема')
	completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата выполнения')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
	urgency_level = models.CharField(max_length=20, choices=URGENCY_LEVELS, default='low', verbose_name='Срочность')
	complexity_level = models.CharField(max_length=20, choices=COMPLEXITY_LEVELS, default='low', verbose_name='Сложность')
	final_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Итоговая цена')
	description = models.TextField(blank=True, null=True, verbose_name='Описание')

	# New fields for technician workflow
	detailed_status = models.CharField(
		max_length=20,
		choices=OrderStatus.choices,
		default=OrderStatus.RECEIVED,
		verbose_name='Детальный статус'
	)
	assigned_to = models.ForeignKey(
		'auth.User',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='assigned_orders',
		verbose_name='Назначен технологу'
	)
	technician_notes = models.TextField(blank=True, null=True, verbose_name='Примечания технолога')
	damage_notes = models.TextField(blank=True, null=True, verbose_name='Отметки о повреждениях')
	recommendations = models.TextField(blank=True, null=True, verbose_name='Рекомендации')

	def __str__(self):
		return f"Заказ {self.id} от {self.client.last_name}"

	class Meta:
		verbose_name = 'Заказ'
		verbose_name_plural = 'Заказы'
