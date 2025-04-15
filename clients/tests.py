import time
import unittest

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from branches.models import Branch
from orders.models import Order, ServiceType
from .models import Client


class ClientModelTest(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testclient', password='testpass123')
		self.client_profile = Client.objects.create(
			user=self.user,
			last_name='Иванов',
			first_name='Иван',
			patronymic='Иванович',
			phone='+79123456789'
		)

	def test_client_creation(self):
		"""Test that a client can be created correctly"""
		self.assertEqual(self.client_profile.user.username, 'testclient')
		self.assertEqual(self.client_profile.last_name, 'Иванов')
		self.assertEqual(self.client_profile.first_name, 'Иван')
		self.assertEqual(self.client_profile.patronymic, 'Иванович')
		self.assertEqual(self.client_profile.phone, '+79123456789')
		self.assertEqual(str(self.client_profile), 'Иванов Иван Иванович')

	def test_client_is_regular_property_with_less_than_three_orders(self):
		"""Test that a client with less than 3 orders is not considered regular"""
		# Create a service type and a branch for orders
		service = ServiceType.objects.create(
			name='Тестовая услуга',
			base_price=100,
			complexity_multiplier=1.0,
			urgency_multiplier=1.0
		)
		branch = Branch.objects.create(name='Главный офис', address='ул. Тестовая, 1')

		# Create 2 orders for the client
		for i in range(2):
			Order.objects.create(
				client=self.client_profile,
				service_type=service,
				branch=branch,
				final_price=100,
				status='completed'
			)

		# Client should not be regular with just 2 orders
		self.assertFalse(self.client_profile.is_regular)

	def test_client_is_regular_property_with_three_or_more_orders(self):
		"""Test that a client with 3 or more orders is considered regular"""
		# Create a service type and a branch for orders
		service = ServiceType.objects.create(
			name='Тестовая услуга',
			base_price=100,
			complexity_multiplier=1.0,
			urgency_multiplier=1.0
		)
		branch = Branch.objects.create(name='Главный офис', address='ул. Тестовая, 1')

		# Create 3 orders for the client
		for i in range(3):
			Order.objects.create(
				client=self.client_profile,
				service_type=service,
				branch=branch,
				final_price=100,
				status='completed'
			)

		# Client should be regular with 3 orders
		self.assertTrue(self.client_profile.is_regular)


class ClientViewTest(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testclient', password='testpass123')
		self.client.login(username='testclient', password='testpass123')

	def test_create_client_profile_view(self):
		"""Test that a user can create a client profile"""
		url = reverse('create_client_profile')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

		# Post data to create a profile
		data = {
			'last_name': 'Петров',
			'first_name': 'Петр',
			'patronymic': 'Петрович',
			'phone': '+79876543210',
			'email': 'test@example.com'
		}
		response = self.client.post(url, data)

		# Should redirect after successful creation
		self.assertEqual(response.status_code, 302)

		# Verify that the client profile was created
		self.assertTrue(Client.objects.filter(user=self.user).exists())
		client_profile = Client.objects.get(user=self.user)
		self.assertEqual(client_profile.last_name, 'Петров')
		self.assertEqual(client_profile.phone, '+79876543210')


class PageNavigationTest(unittest.TestCase):
	def setUp(self):
		options = webdriver.ChromeOptions()
		# options.add_argument('--headless')  # отключено для наглядности
		self.driver = webdriver.Chrome(options=options)
		self.driver.maximize_window()
		self.driver.get('http://127.0.0.1:8000')

	def test_page_views(self):
		driver = self.driver
		
		driver.find_element(By.LINK_TEXT, "Вход").click()
		driver.find_element(By.ID, "id_username").send_keys("admin")
		driver.find_element(By.ID, "id_password").send_keys("admin")
		driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
		WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "Оформить заказ")))

		# Главная
		driver.get("http://127.0.0.1:8000/")
		time.sleep(2)  # пауза для наблюдения
		self.assertIn("Химчистка", driver.page_source)

		# Прайс-лист
		driver.get("http://127.0.0.1:8000/services/prices/")
		time.sleep(2)  # пауза для наблюдения
		self.assertIn("Прайс-лист услуг", driver.page_source)

		# Филиалы
		driver.get("http://127.0.0.1:8000/branches/branches/")
		time.sleep(2)  # пауза для наблюдения
		self.assertIn("Наши филиалы", driver.page_source)

		# Кабинет заказов
		driver.get("http://127.0.0.1:8000/orders/dashboard/")
		time.sleep(2)  # пауза для наблюдения
		self.assertIn("Мои заказы", driver.page_source)

	def tearDown(self):
		time.sleep(2)  # пауза для наблюдения
		self.driver.quit()
