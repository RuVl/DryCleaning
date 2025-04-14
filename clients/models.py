from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from branches.models import Branch


class Client(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
	last_name = models.CharField(max_length=100, verbose_name="Фамилия")
	first_name = models.CharField(max_length=100, verbose_name="Имя")
	patronymic = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")
	phone = models.CharField(max_length=20, verbose_name="Телефон")
	address = models.TextField(blank=True, null=True, verbose_name="Адрес")
	created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата регистрации")
	email = models.EmailField(blank=True)
	visits_count = models.PositiveIntegerField(default=0)

	@property
	def is_regular(self):
		"""Постоянный клиент (от 3 заказов)"""
		from orders.models import Order
		return Order.objects.filter(client=self).count() >= 3

	@property
	def discount(self):
		"""Скидка для постоянного клиента"""
		return 3 if self.is_regular else 0

	@property
	def full_name(self):
		if self.patronymic:
			return f"{self.last_name} {self.first_name} {self.patronymic}"
		return f"{self.last_name} {self.first_name}"

	def __str__(self):
		return self.full_name

	class Meta:
		verbose_name = "Клиент"
		verbose_name_plural = "Клиенты"
