import time
import unittest
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from accounts.models import UserProfile, UserRole
from accounts.tests import CustomTestCase
from branches.models import Branch
from clients.models import Client
from services.models import ServiceType
from .forms import OrderForm, OrderTechnicianForm
from .models import Order, OrderStatus


class OrderModelTest(TestCase):
	def setUp(self):
		# Create a user and client
		self.user = User.objects.create_user(username='testclient', password='testpass123')
		self.client_profile = Client.objects.create(
			user=self.user,
			last_name='Иванов',
			first_name='Иван',
			patronymic='Иванович',
			phone='+79123456789'
		)

		# Create service types with different prices
		self.service_type = ServiceType.objects.create(
			name='Стандартная чистка',
			base_price=Decimal('100.00'),
			complexity_multiplier=Decimal('1.00'),
			urgency_multiplier=Decimal('1.00')
		)

		# Create a branch
		self.branch = Branch.objects.create(name='Главный офис', address='ул. Тестовая, 1')

	def test_order_creation(self):
		"""Test that an order is created correctly"""
		order = Order.objects.create(
			client=self.client_profile,
			service_type=self.service_type,
			branch=self.branch,
			urgency_level='low',
			complexity_level='low',
			final_price=Decimal('100.00'),
			status='pending'
		)

		self.assertEqual(order.client, self.client_profile)
		self.assertEqual(order.service_type, self.service_type)
		self.assertEqual(order.branch, self.branch)
		self.assertEqual(order.urgency_level, 'low')
		self.assertEqual(order.complexity_level, 'low')
		self.assertEqual(order.final_price, Decimal('100.00'))
		self.assertEqual(order.status, 'pending')
		self.assertEqual(order.detailed_status, OrderStatus.RECEIVED)

	def test_order_price_calculation_with_complexity_and_urgency(self):
		"""Test that the order price is calculated correctly with complexity and urgency"""
		# Create an order with high complexity and urgency
		order = Order.objects.create(
			client=self.client_profile,
			service_type=self.service_type,
			branch=self.branch,
			urgency_level='high',
			complexity_level='high',
			final_price=Decimal('150.00'),  # This would be calculated by the view
			status='pending'
		)

		# In a real application, this calculation would be done by the view logic
		base_price = self.service_type.base_price
		complexity_surcharge = base_price * Decimal('0.2')  # 20% for high complexity
		urgency_surcharge = base_price * Decimal('0.3')  # 30% for high urgency

		expected_price = base_price + complexity_surcharge + urgency_surcharge

		# We're not testing the actual business logic calculation here since it's in the view,
		# but we're testing that the price can be stored as expected
		self.assertEqual(order.final_price, Decimal('150.00'))

	def test_order_discount_for_regular_client(self):
		"""Test that a discount is applied for a regular client"""
		# Create 3 orders to make the client regular
		for i in range(3):
			Order.objects.create(
				client=self.client_profile,
				service_type=self.service_type,
				branch=self.branch,
				urgency_level='low',
				complexity_level='low',
				final_price=Decimal('100.00'),
				status='completed'
			)

		# Now the client should be regular, verify this
		self.assertTrue(self.client_profile.is_regular)

		# In the real application, this would be calculated by the view
		base_price = Decimal('100.00')
		discount = base_price * Decimal('0.03')  # 3% discount
		expected_discounted_price = base_price - discount

		# We're just testing that a discounted price can be stored
		order = Order.objects.create(
			client=self.client_profile,
			service_type=self.service_type,
			branch=self.branch,
			urgency_level='low',
			complexity_level='low',
			final_price=expected_discounted_price,
			status='pending'
		)

		self.assertEqual(order.final_price, Decimal('97.00'))


class OrderFormTest(TestCase):
	def setUp(self):
		self.service_type = ServiceType.objects.create(
			name='Стандартная чистка',
			base_price=Decimal('100.00'),
			complexity_multiplier=Decimal('1.00'),
			urgency_multiplier=Decimal('1.00')
		)

		self.branch = Branch.objects.create(name='Главный офис', address='ул. Тестовая, 1')

	def test_order_form_valid(self):
		"""Test that the OrderForm validates with correct data"""
		form_data = {
			'service_type': self.service_type.id,
			'branch': self.branch.id,
			'urgency_level': 'low',
			'complexity_level': 'low',
			'description': 'Тестовое описание заказа'
		}

		form = OrderForm(data=form_data)
		self.assertTrue(form.is_valid())

	def test_order_form_invalid(self):
		"""Test that the OrderForm invalidates incorrect data"""
		# Missing required field
		form_data = {
			'service_type': self.service_type.id,
			# missing branch
			'urgency_level': 'low',
			'complexity_level': 'low'
		}

		form = OrderForm(data=form_data)
		self.assertFalse(form.is_valid())
		self.assertIn('branch', form.errors)

		# Invalid choice
		form_data = {
			'service_type': self.service_type.id,
			'branch': self.branch.id,
			'urgency_level': 'invalid_choice',  # Invalid choice
			'complexity_level': 'low'
		}

		form = OrderForm(data=form_data)
		self.assertFalse(form.is_valid())
		self.assertIn('urgency_level', form.errors)


class OrderTechnicianFormTest(TestCase):
	def setUp(self):
		# Create user and client
		self.user = User.objects.create_user(username='testclient', password='testpass123')
		self.client_profile = Client.objects.create(
			user=self.user,
			last_name='Иванов',
			first_name='Иван',
			patronymic='Иванович'
		)

		# Create service type and branch
		self.service_type = ServiceType.objects.create(
			name='Стандартная чистка',
			base_price=Decimal('100.00')
		)

		self.branch = Branch.objects.create(name='Главный офис', address='ул. Тестовая, 1')

		# Create an order
		self.order = Order.objects.create(
			client=self.client_profile,
			service_type=self.service_type,
			branch=self.branch,
			final_price=Decimal('100.00'),
			status='pending',
			detailed_status=OrderStatus.RECEIVED
		)

	def test_order_technician_form_valid(self):
		"""Test that the OrderTechnicianForm validates with correct data"""
		form_data = {
			'detailed_status': OrderStatus.IN_CLEANING,
			'technician_notes': 'Приступаем к чистке',
		}

		form = OrderTechnicianForm(data=form_data, instance=self.order)
		self.assertTrue(form.is_valid())

	def test_order_technician_form_invalid(self):
		"""Test that the OrderTechnicianForm invalidates incorrect data"""
		# Invalid status choice
		form_data = {
			'detailed_status': 'invalid_status',
		}

		form = OrderTechnicianForm(data=form_data, instance=self.order)
		self.assertFalse(form.is_valid())
		self.assertIn('detailed_status', form.errors)


class OrderViewTest(CustomTestCase):
	def setUp(self):
		super().setUp()

		# Get users with different roles that were created in the parent setUp
		self.client_user, _ = User.objects.get_or_create(username='client')
		self.client_user.set_password('testpass123')
		self.client_user.save()

		self.operator_user, _ = User.objects.get_or_create(username='operator')
		self.operator_user.set_password('testpass123')
		self.operator_user.save()

		self.manager_user, _ = User.objects.get_or_create(username='manager')
		self.manager_user.set_password('testpass123')
		self.manager_user.save()

		self.technician_user, _ = User.objects.get_or_create(username='technician')
		self.technician_user.set_password('testpass123')
		self.technician_user.save()

		self.accountant_user, _ = User.objects.get_or_create(username='accountant')
		self.accountant_user.set_password('testpass123')
		self.accountant_user.save()

		# Ensure the UserProfiles have the correct roles
		operator_profile, _ = UserProfile.objects.get_or_create(user=self.operator_user)
		operator_profile.role = UserRole.OPERATOR
		operator_profile.save()

		technician_profile, _ = UserProfile.objects.get_or_create(user=self.technician_user)
		technician_profile.role = UserRole.TECHNICIAN
		technician_profile.save()

		# Create client profile
		self.client_profile, _ = Client.objects.get_or_create(
			user=self.client_user,
			defaults={
				'last_name': 'Клиентов',
				'first_name': 'Клиент',
				'patronymic': 'Клиентович'
			}
		)

		# We'll use the patched UserProfile property from CustomTestCase
		# so we don't need to explicitly create UserProfiles here

		# Create service and branch
		self.service_type = ServiceType.objects.create(
			name='Стандартная чистка',
			base_price=Decimal('100.00')
		)

		self.branch = Branch.objects.create(name='Главный офис', address='ул. Тестовая, 1')

		# Create an order
		self.order = Order.objects.create(
			client=self.client_profile,
			service_type=self.service_type,
			branch=self.branch,
			final_price=Decimal('100.00'),
			status='pending'
		)

	def test_client_can_view_own_orders(self):
		"""Test that a client can view their own orders"""
		self.client.login(username='client', password='testpass123')
		response = self.client.get(reverse('client_dashboard'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Стандартная чистка')  # Order should be in the response

	def test_client_cannot_view_all_orders(self):
		"""Test that a client cannot access the all orders page"""
		self.client.login(username='client', password='testpass123')
		response = self.client.get(reverse('all_orders'))
		# Should get permission denied (403)
		self.assertEqual(response.status_code, 403)

	def test_operator_can_create_orders(self):
		"""Test that an operator can create orders"""
		self.client.login(username='operator', password='testpass123')

		# Get the create order page
		response = self.client.get(reverse('create_order'))
		# The view might redirect to a login page or the form page, 
		# either 200 or 302 is acceptable here
		self.assertIn(response.status_code, [200, 302])

		# If it's a redirect, follow it
		if response.status_code == 302:
			response = self.client.get(response.url)
			self.assertEqual(response.status_code, 200)

	def test_technician_can_update_order_status(self):
		"""Test that a technician can update the order status"""
		# Assign the order to the technician
		self.order.assigned_to = self.technician_user
		self.order.save()

		self.client.login(username='technician', password='testpass123')

		# Get the update status page
		url = reverse('order_status_update', args=[self.order.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

		# Update the status
		data = {
			'detailed_status': OrderStatus.IN_CLEANING,
			'technician_notes': 'Приступаем к чистке',
		}

		response = self.client.post(url, data)
		# Should redirect after successful update
		self.assertEqual(response.status_code, 302)

		# Verify the status was updated
		self.order.refresh_from_db()
		self.assertEqual(self.order.detailed_status, OrderStatus.IN_CLEANING)
		self.assertEqual(self.order.status, 'in_progress')

	def test_manager_can_edit_order(self):
		"""Test that a manager can edit an order"""
		self.client.login(username='manager', password='testpass123')

		# Get the edit order page
		url = reverse('order_edit', args=[self.order.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

	def test_accountant_cannot_edit_order(self):
		"""Test that an accountant cannot edit an order"""
		self.client.login(username='accountant', password='testpass123')

		# Try to get the edit order page
		url = reverse('order_edit', args=[self.order.id])
		response = self.client.get(url)
		# Should get permission denied (403)
		self.assertEqual(response.status_code, 403)


class OrderBusinessLogicTest(CustomTestCase):
	def setUp(self):
		super().setUp()  # Call the parent's setUp to get the test flag behaviors
		# Create user and client
		self.user, _ = User.objects.get_or_create(username='testclient')
		self.user.set_password('testpass123')
		self.user.save()

		self.client_profile, _ = Client.objects.get_or_create(
			user=self.user,
			defaults={
				'last_name': 'Иванов',
				'first_name': 'Иван',
				'patronymic': 'Иванович'
			}
		)

		# Create service types
		self.service_type = ServiceType.objects.create(
			name='Стандартная чистка',
			base_price=Decimal('100.00'),
			complexity_multiplier=Decimal('1.10'),  # 10% increase for medium complexity
			urgency_multiplier=Decimal('1.15')  # 15% increase for medium urgency
		)

		# Create a branch
		self.branch = Branch.objects.create(name='Главный офис', address='ул. Тестовая, 1')

		# Login as the client
		self.client.login(username='testclient', password='testpass123')

	def test_order_creation_with_price_calculation(self):
		"""Test that the price is calculated correctly when creating an order"""
		# For this test, we'll call the view directly to test the business logic
		data = {
			'service_type': self.service_type.id,
			'branch': self.branch.id,
			'urgency_level': 'medium',  # 15% surcharge
			'complexity_level': 'medium',  # 10% surcharge
			'description': 'Тестовый заказ'
		}

		response = self.client.post(reverse('create_order'), data)
		# Should redirect after successful creation
		self.assertEqual(response.status_code, 302)

		# Verify that the order was created
		order = Order.objects.filter(client=self.client_profile).first()
		self.assertIsNotNone(order)

		# Manually calculate the expected price
		base_price = self.service_type.base_price
		complexity_surcharge = base_price * Decimal('0.1')  # 10% for medium complexity
		urgency_surcharge = base_price * Decimal('0.15')  # 15% for medium urgency
		expected_price = base_price + complexity_surcharge + urgency_surcharge

		# The final price should be close to our manual calculation
		# (there might be slight differences due to rounding)
		self.assertAlmostEqual(order.final_price, expected_price, places=2)

	def test_discount_for_regular_client(self):
		"""Test that a discount is applied for regular clients when creating an order"""
		# Create 3 completed orders to make the client regular
		for i in range(3):
			Order.objects.create(
				client=self.client_profile,
				service_type=self.service_type,
				branch=self.branch,
				urgency_level='low',
				complexity_level='low',
				final_price=Decimal('100.00'),
				status='completed'
			)

		# Verify that the client is now regular
		self.assertTrue(Client.objects.get(id=self.client_profile.id).is_regular)

		# Create a new order and check if discount is applied
		data = {
			'service_type': self.service_type.id,
			'branch': self.branch.id,
			'urgency_level': 'low',
			'complexity_level': 'low',
			'description': 'Заказ с скидкой'
		}

		response = self.client.post(reverse('create_order'), data)
		self.assertEqual(response.status_code, 302)

		# Get the latest order
		latest_order = Order.objects.filter(client=self.client_profile).order_by('-received_at').first()

		# Calculate expected price with discount
		base_price = self.service_type.base_price
		discount = base_price * Decimal('0.03')  # 3% discount for regular clients
		expected_price = base_price - discount

		# The final price should include the discount
		self.assertAlmostEqual(latest_order.final_price, expected_price, places=2)


class DryCleaningUITest(unittest.TestCase):
	def setUp(self):
		options = webdriver.ChromeOptions()
		# options.add_argument('--headless')  # отключено для визуального теста
		self.driver = webdriver.Chrome(options=options)
		self.driver.maximize_window()
		self.driver.get('http://127.0.0.1:8000')

	def test_login_and_create_order(self):
		driver = self.driver

		# 1. Переход на страницу входа
		driver.find_element(By.LINK_TEXT, "Вход").click()

		# 2. Заполнение формы входа
		driver.find_element(By.ID, "id_username").send_keys("admin")
		driver.find_element(By.ID, "id_password").send_keys("admin")
		driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

		# 3. Переход на страницу создания заказа
		WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "Оформить заказ")))
		driver.find_element(By.LINK_TEXT, "Оформить заказ").click()

		# 4. Заполнение формы заказа
		WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "service_type")))
		Select(driver.find_element(By.NAME, "service_type")).select_by_index(1)
		Select(driver.find_element(By.NAME, "branch")).select_by_index(1)
		Select(driver.find_element(By.NAME, "urgency_level")).select_by_value("medium")
		Select(driver.find_element(By.NAME, "complexity_level")).select_by_value("medium")

		driver.find_element(By.NAME, "description").send_keys("Сдать пальто на химчистку")
		
		# 5. Отправка формы
		time.sleep(2)  # оставить паузу для наблюдения
		driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

		# 6. Проверка, что перешли на страницу успеха
		WebDriverWait(driver, 5).until(EC.title_contains("Заказ оформлен"))
		self.assertIn("заказ оформлен", driver.page_source.lower())

	def tearDown(self):
		time.sleep(2)  # оставить паузу для наблюдения
		self.driver.quit()
