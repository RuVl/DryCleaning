from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

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
