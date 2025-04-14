# Create your tests here.

from django.test import TestCase
from django.urls import reverse

from .models import Branch


class BranchModelTest(TestCase):
	def setUp(self):
		# Create some branches for testing
		self.branch1 = Branch.objects.create(
			name='Главный офис',
			address='ул. Центральная, 1',
			phone='+79991234567',
			opening_hours='Пн-Пт: 9:00-18:00, Сб: 10:00-16:00'
		)

		self.branch2 = Branch.objects.create(
			name='Филиал Юг',
			address='ул. Южная, 15',
			phone='+79997654321',
			opening_hours='Пн-Пт: 10:00-19:00'
		)

	def test_branch_creation(self):
		"""Test that branches are created correctly"""
		self.assertEqual(self.branch1.name, 'Главный офис')
		self.assertEqual(self.branch1.address, 'ул. Центральная, 1')
		self.assertEqual(self.branch1.phone, '+79991234567')
		self.assertEqual(self.branch1.opening_hours, 'Пн-Пт: 9:00-18:00, Сб: 10:00-16:00')

		self.assertEqual(self.branch2.name, 'Филиал Юг')
		self.assertEqual(self.branch2.address, 'ул. Южная, 15')
		self.assertEqual(self.branch2.phone, '+79997654321')
		self.assertEqual(self.branch2.opening_hours, 'Пн-Пт: 10:00-19:00')

	def test_branch_string_representation(self):
		"""Test the string representation of branches"""
		self.assertEqual(str(self.branch1), 'Главный офис')
		self.assertEqual(str(self.branch2), 'Филиал Юг')

	def test_branches_list_view(self):
		"""Test the view that displays the list of branches"""
		url = reverse('branches')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

		# Check that both branches are in the response
		self.assertContains(response, 'Главный офис')
		self.assertContains(response, 'Филиал Юг')
		self.assertContains(response, 'ул. Центральная, 1')
		self.assertContains(response, 'ул. Южная, 15')

	def test_branch_detail_view(self):
		"""Test the view that displays branch details"""
		url = reverse('branch_detail', args=[self.branch1.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

		# Check that branch details are in the response
		self.assertContains(response, 'Главный офис')
		self.assertContains(response, 'ул. Центральная, 1')
		self.assertContains(response, '+79991234567')
		self.assertContains(response, 'Пн-Пт: 9:00-18:00, Сб: 10:00-16:00')
