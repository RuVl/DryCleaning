import time
import unittest
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from .models import ServiceType


class ServiceTypeTest(TestCase):
	def setUp(self):
		# Create some service types for testing
		self.service1 = ServiceType.objects.create(
			name='Стандартная чистка',
			category='Одежда',
			base_price=Decimal('100.00'),
			complexity_multiplier=Decimal('1.00'),
			urgency_multiplier=Decimal('1.00')
		)

		self.service2 = ServiceType.objects.create(
			name='Премиум чистка',
			category='Верхняя одежда',
			base_price=Decimal('200.00'),
			complexity_multiplier=Decimal('1.50'),
			urgency_multiplier=Decimal('1.30')
		)

	def test_service_type_creation(self):
		"""Test that service types are created correctly"""
		self.assertEqual(self.service1.name, 'Стандартная чистка')
		self.assertEqual(self.service1.category, 'Одежда')
		self.assertEqual(self.service1.base_price, Decimal('100.00'))
		self.assertEqual(self.service1.complexity_multiplier, Decimal('1.00'))
		self.assertEqual(self.service1.urgency_multiplier, Decimal('1.00'))

		self.assertEqual(self.service2.name, 'Премиум чистка')
		self.assertEqual(self.service2.category, 'Верхняя одежда')
		self.assertEqual(self.service2.base_price, Decimal('200.00'))
		self.assertEqual(self.service2.complexity_multiplier, Decimal('1.50'))
		self.assertEqual(self.service2.urgency_multiplier, Decimal('1.30'))

	def test_service_type_string_representation(self):
		"""Test the string representation of service types"""
		self.assertEqual(str(self.service1), 'Стандартная чистка (Одежда)')
		self.assertEqual(str(self.service2), 'Премиум чистка (Верхняя одежда)')

	def test_service_price_list_view(self):
		"""Test the view that displays the service price list"""
		url = reverse('price_list')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

		# Check that both services are in the response
		self.assertContains(response, 'Стандартная чистка')
		self.assertContains(response, 'Премиум чистка')
		self.assertContains(response, '100.00')
		self.assertContains(response, '200.00')

	def test_service_ordering(self):
		"""Test that services are ordered correctly"""
		services = ServiceType.objects.all().order_by('name')
		self.assertEqual(services[0].name, 'Премиум чистка')
		self.assertEqual(services[1].name, 'Стандартная чистка')


class PriceListPageTest(unittest.TestCase):
	def setUp(self):
		options = webdriver.ChromeOptions()
		# options.add_argument('--headless')  # отключено для наглядности
		self.driver = webdriver.Chrome(options=options)
		self.driver.maximize_window()
		self.driver.get('http://127.0.0.1:8000')

	def login_as_admin(self):
		driver = self.driver
		driver.find_element(By.LINK_TEXT, "Вход").click()
		driver.find_element(By.ID, "id_username").send_keys("admin")
		driver.find_element(By.ID, "id_password").send_keys("admin")
		driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
		WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "Оформить заказ")))

	def test_price_list_and_calculator(self):
		driver = self.driver
		self.login_as_admin()

		# Переход на страницу прайс-листа
		driver.get("http://127.0.0.1:8000/services/prices/")
		WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "serviceSelect")))

		# Проверка, что калькулятор есть на странице
		self.assertIn("Калькулятор стоимости", driver.page_source)
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(1)

		# Выбор услуги
		select = Select(driver.find_element(By.ID, "serviceSelect"))
		select.select_by_index(1)

		# Включение срочности, сложности и статуса "постоянный клиент"
		driver.find_element(By.ID, "urgencyCheck").click()
		driver.find_element(By.ID, "complexityCheck").click()
		driver.find_element(By.ID, "regularClientCheck").click()

		# Нажатие на кнопку расчета
		driver.find_element(By.ID, "calculateBtn").click()

		# Проверка, что результат расчета отображается
		WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "resultBox")))
		result_box = driver.find_element(By.ID, "resultBox")
		self.assertIn("Итоговая стоимость", result_box.text)

		# Можно проверить, что сумма > 0 (базовая цена + надбавки - скидка)
		total_price = result_box.find_element(By.ID, "totalPrice").text
		self.assertGreater(float(total_price.replace(",", ".").strip()), 0)

	def tearDown(self):
		time.sleep(2)
		self.driver.quit()
