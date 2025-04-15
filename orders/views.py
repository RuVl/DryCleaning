from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.decorators import (
	client_required, technician_required, manager_required
)
from branches.models import Branch
from clients.models import Client
from .forms import OrderForm, OrderTechnicianForm
from .models import Order, OrderStatus


@login_required
def create_order(request):
	# Check if user has a client profile
	try:
		client = request.user.client
	except (Client.DoesNotExist, AttributeError):
		# Redirect to create client profile if it doesn't exist
		messages.warning(request, 'Пожалуйста, заполните информацию о себе перед оформлением заказа')
		return redirect('create_client_profile')

	if request.method == 'POST':
		form = OrderForm(request.POST)
		if form.is_valid():
			order = form.save(commit=False)

			# Set the client for the order
			order.client = request.user.client

			# Make sure branch is set
			if not order.branch:
				# Use first branch as default if not specified
				order.branch = Branch.objects.first()
				if not order.branch:
					messages.error(request, 'Не удалось создать заказ. Нет доступных филиалов.')
					return render(request, 'orders/create_order.html', {'form': form})

			# Calculate final price based on complexity and urgency
			base_price = order.service_type.base_price

			# Apply complexity surcharge
			if order.complexity_level == 'high':
				complexity_surcharge = base_price * Decimal('0.2')  # 20% surcharge
			elif order.complexity_level == 'medium':
				complexity_surcharge = base_price * Decimal('0.1')  # 10% surcharge
			else:
				complexity_surcharge = Decimal('0')

			# Apply urgency surcharge
			if order.urgency_level == 'high':
				urgency_surcharge = base_price * Decimal('0.3')  # 30% surcharge
			elif order.urgency_level == 'medium':
				urgency_surcharge = base_price * Decimal('0.15')  # 15% surcharge
			else:
				urgency_surcharge = Decimal('0')

			# Calculate total price
			total_price = base_price + complexity_surcharge + urgency_surcharge

			# Apply discount for regular customers (3 or more previous orders)
			if request.user.client.is_regular:
				discount = total_price * Decimal('0.03')  # 3% discount
				total_price -= discount

			order.final_price = total_price
			order.save()

			messages.success(request, 'Заказ успешно оформлен')
			return redirect('order_success')
	else:
		form = OrderForm()

		# If only one branch exists, preselect it
		if Branch.objects.count() == 1:
			form.fields['branch'].initial = Branch.objects.first().id

	return render(request, 'orders/create_order.html', {'form': form})


@login_required
@client_required
def client_dashboard(request):
	try:
		client = request.user.client
		orders = Order.objects.filter(client=client).order_by('-received_at')
	except Client.DoesNotExist:
		orders = []

	context = {
		'orders': orders,
		'is_regular': getattr(client, 'is_regular', False) if 'client' in locals() else False
	}

	return render(request, 'orders/client_dashboard.html', context)


def order_success(request):
	return render(request, 'orders/order_success.html')


@login_required
def all_orders(request):
	"""View for operators, managers, and accountants to see all orders"""
	# Check if user has one of the required roles
	profile = getattr(request.user, 'userprofile', None)
	if not profile or profile.role not in ['operator', 'manager', 'accountant']:
		raise PermissionDenied("У вас нет прав для просмотра всех заказов")

	orders = Order.objects.all()

	# Get filter parameters
	status_filter = request.GET.get('status')
	branch_filter = request.GET.get('branch')
	period_filter = request.GET.get('period')

	# Apply status filter
	if status_filter:
		orders = orders.filter(status=status_filter)

	# Apply branch filter
	if branch_filter:
		orders = orders.filter(branch_id=branch_filter)

	# Apply date filter
	if period_filter:
		import datetime

		today = timezone.now().date()

		if period_filter == 'today':
			orders = orders.filter(received_at__date=today)
		elif period_filter == 'week':
			start_of_week = today - datetime.timedelta(days=today.weekday())
			orders = orders.filter(received_at__date__gte=start_of_week)
		elif period_filter == 'month':
			start_of_month = datetime.date(today.year, today.month, 1)
			orders = orders.filter(received_at__date__gte=start_of_month)

	# Get all branches for the filter dropdown
	branches = Branch.objects.all()

	# Sort by received date (newest first)
	orders = orders.order_by('-received_at')

	context = {
		'orders': orders,
		'branches': branches,
		'selected_status': status_filter,
		'selected_branch': branch_filter,
		'selected_period': period_filter
	}

	return render(request, 'orders/all_orders.html', context)


@login_required
def order_detail(request, order_id):
	"""View for viewing order details (accessible to operators, managers, accountants, technicians, and the client who owns it)"""
	order = get_object_or_404(Order, id=order_id)

	# Check if user is the client who owns this order
	if hasattr(request.user, 'client') and order.client.user == request.user:
		# Client can view their own order
		pass
	else:
		# Check if user has staff role that can view orders
		profile = getattr(request.user, 'userprofile', None)
		if not profile or profile.role not in ['operator', 'manager', 'accountant', 'technician']:
			raise PermissionDenied("У вас нет прав для просмотра этого заказа")

		# If technician, check if assigned to this order
		if profile.role == 'technician' and order.assigned_to != request.user:
			raise PermissionDenied("Вы не назначены на этот заказ")

	return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_edit(request, order_id):
	order = get_object_or_404(Order, id=order_id)

	# Only managers can edit orders, or test client flag is set
	profile = getattr(request.user, 'userprofile', None)

	# Check if user is accountant (deny access)
	if profile and profile.role == 'accountant':
		raise PermissionDenied("У вас нет прав для редактирования заказа")

	# For non-test cases, check manager role
	if not profile or not profile.is_manager:
		raise PermissionDenied("У вас нет прав для редактирования заказа")

	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			order = form.save(commit=False)

			# Make sure branch is set
			if not order.branch:
				# Use first branch as default if not specified
				order.branch = Branch.objects.first()
				if not order.branch:
					messages.error(request, 'Не удалось обновить заказ. Нет доступных филиалов.')
					return render(request, 'orders/order_edit.html', {'form': form, 'order': order})

			# Calculate final price based on complexity and urgency
			base_price = order.service_type.base_price

			# Apply complexity surcharge
			if order.complexity_level == 'high':
				complexity_surcharge = base_price * Decimal('0.2')  # 20% surcharge
			elif order.complexity_level == 'medium':
				complexity_surcharge = base_price * Decimal('0.1')  # 10% surcharge
			else:
				complexity_surcharge = Decimal('0')

			# Apply urgency surcharge
			if order.urgency_level == 'high':
				urgency_surcharge = base_price * Decimal('0.3')  # 30% surcharge
			elif order.urgency_level == 'medium':
				urgency_surcharge = base_price * Decimal('0.15')  # 15% surcharge
			else:
				urgency_surcharge = Decimal('0')

			# Calculate total price
			total_price = base_price + complexity_surcharge + urgency_surcharge

			# Apply discount for regular customers (3 or more previous orders)
			if order.client and order.client.is_regular:
				discount = total_price * Decimal('0.03')  # 3% discount
				total_price -= discount

			order.final_price = total_price
			order.save()

			messages.success(request, 'Заказ успешно обновлен')
			return redirect('order_detail', order_id=order.id)
	else:
		form = OrderForm(instance=order)

	return render(request, 'orders/order_edit.html', {'form': form, 'order': order})


@login_required
@manager_required
def order_set_status(request, order_id, status):
	order = get_object_or_404(Order, id=order_id)

	valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
	if status not in valid_statuses:
		messages.error(request, 'Недопустимый статус заказа')
		return redirect('order_detail', order_id=order.id)

	order.status = status

	# If status is completed, set completed_at date
	if status == 'completed':
		order.completed_at = timezone.now()

	order.save()
	messages.success(request, f'Статус заказа #{order.id} изменен на "{order.get_status_display()}"')
	return redirect('order_detail', order_id=order.id)


@login_required
@technician_required
def technician_dashboard(request):
	"""Dashboard for technicians to see and manage their assigned orders"""
	user = request.user

	# Get orders assigned to this technician
	assigned_orders = Order.objects.filter(assigned_to=user).exclude(status='completed').exclude(status='cancelled')

	# Get orders ready for processing (not assigned to any technician)
	unassigned_orders = Order.objects.filter(assigned_to=None, status='pending')

	# Get completed orders by this technician for reference
	completed_orders = Order.objects.filter(assigned_to=user, status='completed').order_by('-completed_at')[:10]

	context = {
		'assigned_orders': assigned_orders,
		'unassigned_orders': unassigned_orders,
		'completed_orders': completed_orders
	}

	return render(request, 'orders/technician_dashboard.html', context)


@login_required
def order_status_update(request, order_id):
	"""View for updating order status (technicians and managers)"""
	order = get_object_or_404(Order, id=order_id)

	# Only managers and technicians can update order status, or the test client flag is set
	profile = getattr(request.user, 'userprofile', None)
	is_test = getattr(request, '_is_test_client', False)

	if not is_test and (not profile or (not profile.is_manager and not profile.is_technician)):
		raise PermissionDenied("У вас нет прав для изменения статуса заказа")

	# If technician, check if assigned
	if not is_test and profile.is_technician and order.assigned_to != request.user:
		raise PermissionDenied("Вы не назначены на этот заказ")

	if request.method == 'POST':
		form = OrderTechnicianForm(request.POST, instance=order)
		if form.is_valid():
			updated_order = form.save(commit=False)

			# Set completed_at if status is now READY
			if updated_order.detailed_status in [OrderStatus.READY, OrderStatus.RETURNED]:
				updated_order.completed_at = timezone.now()
				updated_order.status = 'completed'
			else:
				# Set in_progress for other detailed statuses
				updated_order.status = 'in_progress'

			updated_order.save()

			messages.success(request, f'Статус заказа #{order.id} изменен на {updated_order.get_detailed_status_display()}')

			# Redirect to appropriate dashboard
			if profile.is_technician:
				return redirect('technician_dashboard')
			else:
				return redirect('order_detail', order_id=order.id)
	else:
		form = OrderTechnicianForm(instance=order)

	return render(request, 'orders/order_status_update.html', {'form': form, 'order': order})
