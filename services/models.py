from django.db import models


class ServiceType(models.Model):
	name = models.CharField(max_length=100, verbose_name="Название услуги")
	category = models.CharField(max_length=100, verbose_name="Категория")  # Химчистка, Глажка и т.п.
	base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Базовая цена")
	complexity_multiplier = models.FloatField(default=1.0, verbose_name="Множитель сложности")
	urgency_multiplier = models.FloatField(default=1.0, verbose_name="Множитель срочности")

	def __str__(self):
		return f"{self.name} ({self.category})"

	class Meta:
		verbose_name = "Тип услуги"
		verbose_name_plural = "Типы услуг"
		ordering = ["category", "name"]
