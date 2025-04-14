from django.db import models


class Branch(models.Model):
	name = models.CharField(max_length=100, verbose_name="Название")
	address = models.CharField(max_length=255, verbose_name="Адрес")
	phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True, default="")
	opening_hours = models.CharField(max_length=255, verbose_name="Часы работы", blank=True, default="")

	def __str__(self):
		return self.name

	@property
	def active_orders_count(self):
		"""Count of active orders (pending or in progress)"""
		return self.orders.filter(status__in=["pending", "in_progress"]).count()

	@property
	def completed_orders_count(self):
		"""Count of completed orders"""
		return self.orders.filter(status="completed").count()

	class Meta:
		verbose_name = "Филиал"
		verbose_name_plural = "Филиалы"
		ordering = ["name"]
