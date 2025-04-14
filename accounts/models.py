from django.contrib.auth.models import User
from django.db import models


class UserRole(models.TextChoices):
	MANAGER = 'manager', 'Менеджер'
	OPERATOR = 'operator', 'Оператор'
	ACCOUNTANT = 'accountant', 'Бухгалтер'
	TECHNICIAN = 'technician', 'Технолог'
	CLIENT = 'client', 'Клиент'


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
	role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CLIENT, verbose_name="Роль")
	branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Филиал")

	def __str__(self):
		return f"{self.user.username} ({self.get_role_display()})"

	@property
	def is_client(self):
		return self.role == UserRole.CLIENT

	@property
	def is_operator(self):
		return self.role == UserRole.OPERATOR

	@property
	def is_manager(self):
		return self.role == UserRole.MANAGER

	@property
	def is_accountant(self):
		return self.role == UserRole.ACCOUNTANT

	@property
	def is_technician(self):
		return self.role == UserRole.TECHNICIAN

	@property
	def can_create_orders(self):
		"""Clients, operators and managers can create orders"""
		return self.is_client or self.is_operator or self.is_manager

	@property
	def can_view_all_clients(self):
		"""Operators, managers and accountants can view client list"""
		return self.is_operator or self.is_manager or self.is_accountant

	@property
	def can_edit_orders(self):
		"""Only managers can edit orders"""
		return self.is_manager

	@property
	def can_delete_orders(self):
		"""Only managers can delete orders"""
		return self.is_manager

	@property
	def can_view_financial_data(self):
		"""Managers and accountants can view financial data"""
		return self.is_manager or self.is_accountant

	@property
	def can_manage_services(self):
		"""Only managers can manage services and branches"""
		return self.is_manager

	@property
	def can_update_order_status(self):
		"""Technicians and managers can update order status"""
		return self.is_technician or self.is_manager

	@property
	def can_add_order_notes(self):
		"""Technicians and managers can add notes to orders"""
		return self.is_technician or self.is_manager

	class Meta:
		verbose_name = "Профиль пользователя"
		verbose_name_plural = "Профили пользователей"
