from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render, redirect

from clients.models import Client
from orders.models import Order
from .decorators import accountant_required
from .forms import UserCreationForm


def register_view(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('home')
	else:
		form = UserCreationForm()
	return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('home')
	return render(request, 'accounts/login.html')


def logout_view(request):
	logout(request)
	return redirect('home')


@login_required
def staff_dashboard(request):
	# Get current date and dates for filtering
	today = datetime.now().date()
	week_ago = today - timedelta(days=7)
	month_ago = today - timedelta(days=30)

	# Active orders
	active_orders = Order.objects.filter(status__in=['pending', 'in_progress']).count()
	active_orders_week_ago = Order.objects.filter(
		status__in=['pending', 'in_progress'],
		received_at__lte=week_ago
	).count()

	# Calculate percentage change
	active_orders_percent = 0
	if active_orders_week_ago > 0:
		active_orders_percent = round(((active_orders - active_orders_week_ago) / active_orders_week_ago) * 100)

	# Completed orders
	completed_orders = Order.objects.filter(status='completed').count()
	completed_orders_month_ago = Order.objects.filter(
		status='completed',
		received_at__lte=month_ago
	).count()

	# Calculate percentage change
	completed_orders_percent = 0
	if completed_orders_month_ago > 0:
		completed_orders_percent = round(((completed_orders - completed_orders_month_ago) / completed_orders_month_ago) * 100)

	# Clients stats
	total_clients = Client.objects.count()
	new_clients = Client.objects.filter(created_at__gte=month_ago).count()

	# Income stats (simplified)
	total_income = Order.objects.filter(status='completed').aggregate(
		total=models.Sum('final_price')
	)['total'] or 0

	# Recent orders
	recent_orders = Order.objects.all().order_by('-received_at')[:10]

	context = {
		'active_orders_count': active_orders,
		'active_orders_percent': active_orders_percent,
		'completed_orders_count': completed_orders,
		'completed_orders_percent': completed_orders_percent,
		'clients_count': total_clients,
		'new_clients_count': new_clients,
		'total_income': total_income,
		'income_percent': 5,  # Placeholder
		'recent_orders': recent_orders,
	}

	return render(request, 'accounts/dashboard.html', context)


@login_required
@accountant_required
def report_daily(request):
	# Get date from request or use today
	date_str = request.GET.get('date')
	if date_str:
		try:
			target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
		except ValueError:
			target_date = datetime.now().date()
	else:
		target_date = datetime.now().date()

	# Get orders for the selected date
	orders = Order.objects.filter(
		received_at__date=target_date
	).order_by('-received_at')

	# Calculate statistics
	total_orders = orders.count()
	completed_orders = orders.filter(status='completed').count()
	pending_orders = orders.filter(status='pending').count()
	in_progress_orders = orders.filter(status='in_progress').count()

	# Calculate income
	daily_income = orders.filter(status='completed').aggregate(
		total=models.Sum('final_price')
	)['total'] or 0

	# Get new clients from that day
	new_clients = Client.objects.filter(
		created_at__date=target_date
	).count()

	context = {
		'orders': orders,
		'target_date': target_date,
		'total_orders': total_orders,
		'completed_orders': completed_orders,
		'pending_orders': pending_orders,
		'in_progress_orders': in_progress_orders,
		'daily_income': daily_income,
		'new_clients': new_clients,
	}

	return render(request, 'accounts/report_daily.html', context)


@login_required
@accountant_required
def report_monthly(request):
	# Get month from request or use current month
	month_str = request.GET.get('month')
	if month_str:
		try:
			year, month = map(int, month_str.split('-'))
			start_date = datetime(year, month, 1).date()
			if month == 12:
				end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
			else:
				end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
		except (ValueError, IndexError):
			today = datetime.now().date()
			start_date = datetime(today.year, today.month, 1).date()
			if today.month == 12:
				end_date = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
			else:
				end_date = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)
	else:
		today = datetime.now().date()
		start_date = datetime(today.year, today.month, 1).date()
		if today.month == 12:
			end_date = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
		else:
			end_date = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)

	# Get orders for the selected month
	orders = Order.objects.filter(
		received_at__date__gte=start_date,
		received_at__date__lte=end_date
	).order_by('-received_at')

	# Calculate statistics
	total_orders = orders.count()
	completed_orders = orders.filter(status='completed').count()
	cancelled_orders = orders.filter(status='cancelled').count()

	# Calculate income
	monthly_income = orders.filter(status='completed').aggregate(
		total=models.Sum('final_price')
	)['total'] or 0

	# Get new clients from that month
	new_clients = Client.objects.filter(
		created_at__date__gte=start_date,
		created_at__date__lte=end_date
	).count()

	# Calculate daily statistics
	daily_stats = []
	current_date = start_date
	while current_date <= end_date:
		day_orders = orders.filter(received_at__date=current_date)
		daily_income = day_orders.filter(status='completed').aggregate(
			total=models.Sum('final_price')
		)['total'] or 0

		daily_stats.append({
			'date': current_date,
			'total_orders': day_orders.count(),
			'completed_orders': day_orders.filter(status='completed').count(),
			'income': daily_income,
		})
		current_date += timedelta(days=1)

	context = {
		'orders': orders,
		'start_date': start_date,
		'end_date': end_date,
		'total_orders': total_orders,
		'completed_orders': completed_orders,
		'cancelled_orders': cancelled_orders,
		'monthly_income': monthly_income,
		'new_clients': new_clients,
		'daily_stats': daily_stats,
		'selected_month': f"{start_date.year}-{start_date.month:02d}",
	}

	return render(request, 'accounts/report_monthly.html', context)


@login_required
@accountant_required
def report_yearly(request):
	# Get year from request or use current year
	year_str = request.GET.get('year')
	if year_str:
		try:
			year = int(year_str)
		except ValueError:
			year = datetime.now().year
	else:
		year = datetime.now().year

	# Calculate start and end dates
	start_date = datetime(year, 1, 1).date()
	end_date = datetime(year, 12, 31).date()

	# Get orders for the selected year
	orders = Order.objects.filter(
		received_at__date__gte=start_date,
		received_at__date__lte=end_date
	).order_by('-received_at')

	# Calculate statistics
	total_orders = orders.count()
	completed_orders = orders.filter(status='completed').count()
	cancelled_orders = orders.filter(status='cancelled').count()

	# Calculate income
	yearly_income = orders.filter(status='completed').aggregate(
		total=models.Sum('final_price')
	)['total'] or 0

	# Get new clients from that year
	new_clients = Client.objects.filter(
		created_at__date__gte=start_date,
		created_at__date__lte=end_date
	).count()

	# Calculate monthly statistics
	monthly_stats = []
	month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
	               'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

	for month in range(1, 13):
		# Calculate start and end dates for each month
		month_start = datetime(year, month, 1).date()
		if month == 12:
			month_end = datetime(year, 12, 31).date()
		else:
			month_end = datetime(year, month + 1, 1).date() - timedelta(days=1)

		# Get orders for this month
		month_orders = orders.filter(
			received_at__date__gte=month_start,
			received_at__date__lte=month_end
		)

		# Calculate monthly income
		month_income = month_orders.filter(status='completed').aggregate(
			total=models.Sum('final_price')
		)['total'] or 0

		# Get new clients for this month
		month_new_clients = Client.objects.filter(
			created_at__date__gte=month_start,
			created_at__date__lte=month_end
		).count()

		monthly_stats.append({
			'month': f"{year}-{month:02d}",
			'month_name': month_names[month - 1],
			'orders_count': month_orders.count(),
			'completed_count': month_orders.filter(status='completed').count(),
			'income': month_income,
			'new_clients': month_new_clients
		})

	# Get top services for the year
	from django.db.models import Count, Sum

	top_services = Order.objects.filter(
		received_at__date__gte=start_date,
		received_at__date__lte=end_date,
		status='completed'
	).values('service_type__name').annotate(
		count=Count('id'),
		income=Sum('final_price')
	).order_by('-count')[:10]

	# Get statistics by branch if branch model exists
	try:
		from branches.models import Branch
		branch_stats = Order.objects.filter(
			received_at__date__gte=start_date,
			received_at__date__lte=end_date,
			status='completed'
		).values('branch__name').annotate(
			orders_count=Count('id'),
			income=Sum('final_price')
		).order_by('-orders_count')
	except ImportError:
		branch_stats = []

	# Get list of available years for the dropdown
	min_year = Order.objects.aggregate(min_year=models.Min('received_at__year'))['min_year'] or year
	current_year = datetime.now().year
	available_years = list(range(min_year, current_year + 1))

	context = {
		'year': year,
		'available_years': available_years,
		'total_orders': total_orders,
		'completed_orders': completed_orders,
		'cancelled_orders': cancelled_orders,
		'yearly_income': yearly_income,
		'new_clients': new_clients,
		'monthly_stats': monthly_stats,
		'top_services': top_services,
		'branch_stats': branch_stats
	}

	return render(request, 'accounts/report_yearly.html', context)


@login_required
@accountant_required
def report_branch(request):
	# Get date range from request or use current month
	period = request.GET.get('period', 'month')
	if period == 'month':
		today = datetime.now().date()
		start_date = datetime(today.year, today.month, 1).date()
		if today.month == 12:
			end_date = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
		else:
			end_date = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)
	elif period == 'year':
		today = datetime.now().date()
		start_date = datetime(today.year, 1, 1).date()
		end_date = datetime(today.year, 12, 31).date()
	elif period == 'week':
		today = datetime.now().date()
		start_date = today - timedelta(days=today.weekday())
		end_date = start_date + timedelta(days=6)
	else:  # all time
		start_date = datetime(2000, 1, 1).date()  # arbitrary early date
		end_date = datetime.now().date()

	# Try to get Branch model
	try:
		from branches.models import Branch

		# Get all branches
		branches = Branch.objects.all()

		# Get orders for each branch in the selected period
		branch_stats = []

		for branch in branches:
			branch_orders = Order.objects.filter(
				branch=branch,
				received_at__date__gte=start_date,
				received_at__date__lte=end_date
			)

			# Calculate statistics
			total_orders = branch_orders.count()
			completed_orders = branch_orders.filter(status='completed').count()

			# Calculate income
			income = branch_orders.filter(status='completed').aggregate(
				total=models.Sum('final_price')
			)['total'] or 0

			# Calculate average processing time (if completed orders exist)
			avg_processing_time = None
			completed_with_dates = branch_orders.filter(
				status='completed',
				completed_at__isnull=False
			)

			if completed_with_dates.exists():
				total_hours = 0
				count = 0

				for order in completed_with_dates:
					if order.completed_at and order.received_at:
						delta = order.completed_at - order.received_at
						total_hours += delta.total_seconds() / 3600
						count += 1

				if count > 0:
					avg_processing_time = round(total_hours / count, 1)

			branch_stats.append({
				'branch': branch,
				'total_orders': total_orders,
				'completed_orders': completed_orders,
				'income': income,
				'avg_processing_time': avg_processing_time
			})

		# Sort branches by total orders (descending)
		branch_stats.sort(key=lambda x: x['total_orders'], reverse=True)

		context = {
			'branch_stats': branch_stats,
			'period': period,
			'start_date': start_date,
			'end_date': end_date
		}

		return render(request, 'accounts/report_branch.html', context)

	except ImportError:
		# Branch model doesn't exist, redirect to dashboard
		return redirect('staff_dashboard')


@login_required
@accountant_required
def report_services(request):
	# Get services statistics
	from django.db.models import Count, Sum
	from services.models import ServiceType

	# Filter period if requested
	period = request.GET.get('period', 'all')
	if period == 'month':
		today = datetime.now().date()
		start_date = datetime(today.year, today.month, 1).date()
	elif period == 'week':
		today = datetime.now().date()
		start_date = today - timedelta(days=today.weekday())
	elif period == 'year':
		today = datetime.now().date()
		start_date = datetime(today.year, 1, 1).date()
	else:
		start_date = None

	# Define the filter for annotate
	if start_date:
		order_filter = models.Q(
			order__status='completed',
			order__received_at__date__gte=start_date
		)
	else:
		order_filter = models.Q(order__status='completed')

	# Get services and their statistics
	services = ServiceType.objects.annotate(
		orders_count=Count('order', filter=order_filter),
		total_income=Sum('order__final_price', filter=order_filter)
	).order_by('-orders_count')

	# Calculate total orders and income
	total_orders = sum(s.orders_count for s in services)
	total_income = sum(s.total_income or 0 for s in services)

	# Add percentage to each service and calculate average price
	for service in services:
		if total_orders > 0:
			service.percentage = round((service.orders_count / total_orders) * 100)
		else:
			service.percentage = 0

		if not service.total_income:
			service.total_income = 0

		# Calculate average check for this service
		if service.orders_count > 0:
			service.avg_check = round(service.total_income / service.orders_count, 2)
		else:
			service.avg_check = 0

	context = {
		'services': services,
		'total_orders': total_orders,
		'total_income': total_income,
		'period': period,
	}

	return render(request, 'accounts/report_services.html', context)
