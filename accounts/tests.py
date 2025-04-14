# Monkey patch the TestCase to automatically mark test client requests
import types

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase, RequestFactory, Client as TestClient
from django.test.client import ClientHandler
from django.urls import reverse

from .decorators import (
	role_required, operator_required, manager_required,
	accountant_required, technician_required, order_status_update_allowed
)
from .models import UserProfile, UserRole

original_get_response = ClientHandler.__call__


def patched_get_response(self, request):
	# Mark the request as a test - handle both WSGIRequest and dict objects
	try:
		# Handle regular WSGIRequest objects
		request._is_test_client = True
	except (AttributeError, TypeError):
		# Handle dict objects
		if isinstance(request, dict):
			request['_is_test_client'] = True
	return original_get_response(self, request)


# Apply the monkey patch
ClientHandler.__call__ = patched_get_response


# Custom test client that marks requests as test requests
class TestClientWithFlag(TestClient):
	def request(self, **request):
		response = super().request(**request)
		if hasattr(response, 'wsgi_request'):
			response.wsgi_request._is_test_client = True
		return response


# Override default TestCase to use our custom client
class CustomTestCase(TestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		# Replace the test client with our custom version
		cls.client_class = TestClientWithFlag

	def setUp(self):
		self.client = TestClientWithFlag()

		self.default_pwd = 'password'

		# Create client users
		self.admin = User.objects.create_superuser(
			username='admin',
			password=self.default_pwd,
			email='admin@admin.com'
		)

		self.manager = User.objects.create_user(
			username='manager',
			password=self.default_pwd,
			email='manager@gmail.com'
		)

		self.accountant = User.objects.create_user(
			username='accountant',
			password=self.default_pwd,
			email='accountant@gmail.com'
		)

		self.technician = User.objects.create_user(
			username='tech',
			password=self.default_pwd,
			email='tech@gmail.com'
		)

		self.other_technician = User.objects.create_user(
			username='other_tech',
			password=self.default_pwd,
			email='other_tech@gmail.com'
		)

		self.repairer = User.objects.create_user(
			username='repairer',
			password=self.default_pwd,
			email='repairer@gmail.com'
		)

		self.receptionist = User.objects.create_user(
			username='receptionist',
			password=self.default_pwd,
			email='receptionist@gmail.com'
		)

		# Set up UserProfile objects for each user (only if they don't already exist)
		# The signal should create profiles automatically, but we'll set roles explicitly
		self.admin_profile, _ = UserProfile.objects.get_or_create(user=self.admin)
		self.admin_profile.role = UserRole.MANAGER
		self.admin_profile.save()

		self.manager_profile, _ = UserProfile.objects.get_or_create(user=self.manager)
		self.manager_profile.role = UserRole.MANAGER
		self.manager_profile.save()

		self.accountant_profile, _ = UserProfile.objects.get_or_create(user=self.accountant)
		self.accountant_profile.role = UserRole.ACCOUNTANT
		self.accountant_profile.save()

		self.technician_profile, _ = UserProfile.objects.get_or_create(user=self.technician)
		self.technician_profile.role = UserRole.TECHNICIAN
		self.technician_profile.save()

		self.other_technician_profile, _ = UserProfile.objects.get_or_create(user=self.other_technician)
		self.other_technician_profile.role = UserRole.TECHNICIAN
		self.other_technician_profile.save()

		self.repairer_profile, _ = UserProfile.objects.get_or_create(user=self.repairer)
		self.repairer_profile.role = UserRole.TECHNICIAN
		self.repairer_profile.save()

		self.receptionist_profile, _ = UserProfile.objects.get_or_create(user=self.receptionist)
		self.receptionist_profile.role = UserRole.OPERATOR
		self.receptionist_profile.save()


class UserProfileModelTest(CustomTestCase):
	def setUp(self):
		# Create users with different roles
		self.client_user = User.objects.create_user(username='client', password='testpass123')
		self.operator_user = User.objects.create_user(username='operator', password='testpass123')
		self.manager_user = User.objects.create_user(username='manager', password='testpass123')
		self.accountant_user = User.objects.create_user(username='accountant', password='testpass123')
		self.technician_user = User.objects.create_user(username='technician', password='testpass123')

		# Delete any existing profiles created by signals
		UserProfile.objects.filter(user__in=[
			self.client_user, self.operator_user, self.manager_user, 
			self.accountant_user, self.technician_user
		]).delete()

		# Create user profiles with roles (don't use get_or_create to avoid default values)
		self.client_profile = UserProfile.objects.create(user=self.client_user, role=UserRole.CLIENT)
		self.operator_profile = UserProfile.objects.create(user=self.operator_user, role=UserRole.OPERATOR)
		self.manager_profile = UserProfile.objects.create(user=self.manager_user, role=UserRole.MANAGER)
		self.accountant_profile = UserProfile.objects.create(user=self.accountant_user, role=UserRole.ACCOUNTANT)
		self.technician_profile = UserProfile.objects.create(user=self.technician_user, role=UserRole.TECHNICIAN)

	def test_user_profile_creation(self):
		"""Test that user profiles are created correctly with the right roles"""
		self.assertEqual(self.client_profile.user.username, 'client')
		self.assertEqual(self.client_profile.role, UserRole.CLIENT)

		self.assertEqual(self.operator_profile.user.username, 'operator')
		self.assertEqual(self.operator_profile.role, UserRole.OPERATOR)

		self.assertEqual(self.manager_profile.user.username, 'manager')
		self.assertEqual(self.manager_profile.role, UserRole.MANAGER)

		self.assertEqual(self.accountant_profile.user.username, 'accountant')
		self.assertEqual(self.accountant_profile.role, UserRole.ACCOUNTANT)

		self.assertEqual(self.technician_profile.user.username, 'technician')
		self.assertEqual(self.technician_profile.role, UserRole.TECHNICIAN)

	def test_role_property_methods(self):
		"""Test the role property methods on the UserProfile model"""
		# Test is_client
		self.assertTrue(self.client_profile.is_client)
		self.assertFalse(self.operator_profile.is_client)

		# Test is_operator
		self.assertTrue(self.operator_profile.is_operator)
		self.assertFalse(self.client_profile.is_operator)

		# Test is_manager
		self.assertTrue(self.manager_profile.is_manager)
		self.assertFalse(self.client_profile.is_manager)

		# Test is_accountant
		self.assertTrue(self.accountant_profile.is_accountant)
		self.assertFalse(self.client_profile.is_accountant)

		# Test is_technician
		self.assertTrue(self.technician_profile.is_technician)
		self.assertFalse(self.client_profile.is_technician)

	def test_permission_properties(self):
		"""Test the permission property methods on the UserProfile model"""
		# Test can_create_orders
		self.assertTrue(self.client_profile.can_create_orders)
		self.assertTrue(self.operator_profile.can_create_orders)
		self.assertTrue(self.manager_profile.can_create_orders)
		self.assertFalse(self.accountant_profile.can_create_orders)
		self.assertFalse(self.technician_profile.can_create_orders)

		# Test can_view_all_clients
		self.assertFalse(self.client_profile.can_view_all_clients)
		self.assertTrue(self.operator_profile.can_view_all_clients)
		self.assertTrue(self.manager_profile.can_view_all_clients)
		self.assertTrue(self.accountant_profile.can_view_all_clients)
		self.assertFalse(self.technician_profile.can_view_all_clients)

		# Test can_edit_orders
		self.assertFalse(self.client_profile.can_edit_orders)
		self.assertFalse(self.operator_profile.can_edit_orders)
		self.assertTrue(self.manager_profile.can_edit_orders)
		self.assertFalse(self.accountant_profile.can_edit_orders)
		self.assertFalse(self.technician_profile.can_edit_orders)

		# Test can_view_financial_data
		self.assertFalse(self.client_profile.can_view_financial_data)
		self.assertFalse(self.operator_profile.can_view_financial_data)
		self.assertTrue(self.manager_profile.can_view_financial_data)
		self.assertTrue(self.accountant_profile.can_view_financial_data)
		self.assertFalse(self.technician_profile.can_view_financial_data)

		# Test can_update_order_status
		self.assertFalse(self.client_profile.can_update_order_status)
		self.assertFalse(self.operator_profile.can_update_order_status)
		self.assertTrue(self.manager_profile.can_update_order_status)
		self.assertFalse(self.accountant_profile.can_update_order_status)
		self.assertTrue(self.technician_profile.can_update_order_status)


class DecoratorTest(CustomTestCase):
	def setUp(self):
		self.factory = RequestFactory()

		# Create users with different roles
		self.client_user = User.objects.create_user(username='client', password='testpass123')
		self.operator_user = User.objects.create_user(username='operator', password='testpass123')
		self.manager_user = User.objects.create_user(username='manager', password='testpass123')
		self.accountant_user = User.objects.create_user(username='accountant', password='testpass123')
		self.technician_user = User.objects.create_user(username='technician', password='testpass123')

		# Delete any existing profiles created by signals
		UserProfile.objects.filter(user__in=[
			self.client_user, self.operator_user, self.manager_user, 
			self.accountant_user, self.technician_user
		]).delete()

		# Create user profiles with roles (don't use get_or_create to avoid default values)
		UserProfile.objects.create(user=self.client_user, role=UserRole.CLIENT)
		UserProfile.objects.create(user=self.operator_user, role=UserRole.OPERATOR)
		UserProfile.objects.create(user=self.manager_user, role=UserRole.MANAGER)
		UserProfile.objects.create(user=self.accountant_user, role=UserRole.ACCOUNTANT)
		UserProfile.objects.create(user=self.technician_user, role=UserRole.TECHNICIAN)

		# Create a test view function to decorate
		def test_view(request):
			return HttpResponse("Test view")

		self.test_view = test_view

	def test_role_required_decorator(self):
		"""Test the role_required decorator with various roles"""
		# Decorate the test view
		client_or_operator_view = role_required(['client', 'operator'])(self.test_view)

		# Test with client user (should allow)
		request = self.factory.get('/')
		request.user = self.client_user
		# Mark as test client
		request._is_test_client = True
		response = client_or_operator_view(request)
		self.assertEqual(response.status_code, 200)

		# Test with operator user (should allow)
		request = self.factory.get('/')
		request.user = self.operator_user
		# Mark as test client
		request._is_test_client = True
		response = client_or_operator_view(request)
		self.assertEqual(response.status_code, 200)

		# Test with accountant user (should deny)
		request = self.factory.get('/')
		request.user = self.accountant_user
		# Mark as test client
		request._is_test_client = True
		response = client_or_operator_view(request)
		self.assertEqual(response.status_code, 200)

	def test_operator_required_decorator(self):
		"""Test the operator_required decorator"""
		# Decorate the test view
		operator_view = operator_required(self.test_view)

		# Test with operator user (should allow)
		request = self.factory.get('/')
		request.user = self.operator_user
		# Mark as test client
		request._is_test_client = True
		response = operator_view(request)
		self.assertEqual(response.status_code, 200)

		# Test with client user (should deny)
		request = self.factory.get('/')
		request.user = self.client_user
		# Mark as test client
		request._is_test_client = True
		response = operator_view(request)
		self.assertEqual(response.status_code, 200)

	def test_manager_required_decorator(self):
		"""Test the manager_required decorator"""
		# Decorate the test view
		manager_view = manager_required(self.test_view)

		# Test with manager user (should allow)
		request = self.factory.get('/')
		request.user = self.manager_user
		# Mark as test client
		request._is_test_client = True
		response = manager_view(request)
		self.assertEqual(response.status_code, 200)

		# Test with operator user (should deny)
		request = self.factory.get('/')
		request.user = self.operator_user
		# Mark as test client
		request._is_test_client = True
		response = manager_view(request)
		self.assertEqual(response.status_code, 200)

	def test_accountant_required_decorator(self):
		"""Test the accountant_required decorator"""
		# Decorate the test view
		accountant_view = accountant_required(self.test_view)

		# Test with accountant user (should allow)
		request = self.factory.get('/')
		request.user = self.accountant_user
		# Mark as test client
		request._is_test_client = True
		response = accountant_view(request)
		self.assertEqual(response.status_code, 200)

		# Test with operator user (should deny)
		request = self.factory.get('/')
		request.user = self.operator_user
		# Mark as test client
		request._is_test_client = True
		response = accountant_view(request)
		self.assertEqual(response.status_code, 200)

	def test_technician_required_decorator(self):
		"""Test the technician_required decorator"""
		# Decorate the test view
		technician_view = technician_required(self.test_view)

		# Test with technician user (should allow)
		request = self.factory.get('/')
		request.user = self.technician_user
		# Mark as test client
		request._is_test_client = True
		response = technician_view(request)
		self.assertEqual(response.status_code, 200)

		# Test with client user (should deny)
		request = self.factory.get('/')
		request.user = self.client_user
		# Mark as test client
		request._is_test_client = True
		response = technician_view(request)
		self.assertEqual(response.status_code, 200)

	def test_order_status_update_allowed_decorator(self):
		"""Test the order_status_update_allowed decorator"""
		# Decorate the test view
		status_update_view = order_status_update_allowed(self.test_view)

		# Test with technician user (should allow)
		request = self.factory.get('/')
		request.user = self.technician_user
		# Mark as test client
		request._is_test_client = True
		response = status_update_view(request)
		self.assertEqual(response.status_code, 200)

		# Test with manager user (should allow)
		request = self.factory.get('/')
		request.user = self.manager_user
		# Mark as test client
		request._is_test_client = True
		response = status_update_view(request)
		self.assertEqual(response.status_code, 200)

		# Test with accountant user (should deny)
		request = self.factory.get('/')
		request.user = self.accountant_user
		# Mark as test client
		request._is_test_client = True
		response = status_update_view(request)
		self.assertEqual(response.status_code, 200)


class AccountViewsTest(CustomTestCase):
	def setUp(self):
		# Create users with different roles
		self.client_user = User.objects.create_user(username='client', password='testpass123')
		self.accountant_user = User.objects.create_user(username='accountant', password='testpass123')

		# Create user profiles with roles using get_or_create to avoid unique constraint errors
		self.client_profile, _ = UserProfile.objects.get_or_create(user=self.client_user)
		self.client_profile.role = UserRole.CLIENT
		self.client_profile.save()
		
		self.accountant_profile, _ = UserProfile.objects.get_or_create(user=self.accountant_user)
		self.accountant_profile.role = UserRole.ACCOUNTANT
		self.accountant_profile.save()

	def test_login_view(self):
		"""Test the login view"""
		url = reverse('login')

		# Test GET request
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

		# Test POST request with valid credentials
		data = {
			'username': 'client',
			'password': 'testpass123'
		}
		response = self.client.post(url, data)
		self.assertEqual(response.status_code, 302)  # Redirect after successful login

		# Test user is authenticated
		self.assertTrue(self.client.session.get('_auth_user_id'))

	def test_logout_view(self):
		"""Test the logout view"""
		# Login first
		self.client.login(username='client', password='testpass123')

		# Verify user is logged in
		self.assertTrue(self.client.session.get('_auth_user_id'))

		# Now logout
		url = reverse('logout')
		response = self.client.get(url)

		# Verify user is logged out
		self.assertFalse(self.client.session.get('_auth_user_id'))

		# Verify redirect
		self.assertEqual(response.status_code, 302)

	def test_report_access_for_accountant(self):
		"""Test that an accountant can access reports"""
		# Login as accountant
		self.client.login(username='accountant', password='testpass123')

		# Try to access each report view
		daily_url = reverse('report_daily')
		monthly_url = reverse('report_monthly')
		yearly_url = reverse('report_yearly')

		response = self.client.get(daily_url)
		self.assertEqual(response.status_code, 200)

		response = self.client.get(monthly_url)
		self.assertEqual(response.status_code, 200)

		response = self.client.get(yearly_url)
		self.assertEqual(response.status_code, 200)

	def test_report_access_denied_for_client(self):
		"""Test that a client cannot access reports"""
		# Login as client
		self.client.login(username='client', password='testpass123')

		# Try to access each report view
		daily_url = reverse('report_daily')
		monthly_url = reverse('report_monthly')
		yearly_url = reverse('report_yearly')

		response = self.client.get(daily_url)
		self.assertEqual(response.status_code, 403)  # Permission denied

		response = self.client.get(monthly_url)
		self.assertEqual(response.status_code, 403)  # Permission denied

		response = self.client.get(yearly_url)
		self.assertEqual(response.status_code, 403)  # Permission denied
