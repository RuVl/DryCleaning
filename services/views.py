from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from accounts.decorators import staff_required
from .forms import ServiceTypeForm
from .models import ServiceType


class ServiceListView(ListView):
	model = ServiceType
	template_name = 'services/list.html'
	context_object_name = 'service_types'

	def get_queryset(self):
		return ServiceType.objects.all().order_by('name')


class PriceListView(ListView):
	model = ServiceType
	template_name = 'services/price_list.html'
	context_object_name = 'service_types'

	def get_queryset(self):
		return ServiceType.objects.all().order_by('category', 'name')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['urgency_surcharge'] = 30  # 30% surcharge for urgent orders
		context['complexity_surcharge'] = 20  # 20% surcharge for complex work
		context['regular_discount'] = 3  # 3% discount for regular clients
		return context


@login_required
@staff_required
def service_create(request):
	if request.method == 'POST':
		form = ServiceTypeForm(request.POST)
		if form.is_valid():
			service = form.save()
			messages.success(request, f'Услуга "{service.name}" успешно создана')
			return redirect('service_types')
	else:
		form = ServiceTypeForm()

	return render(request, 'services/service_form.html', {
		'form': form,
		'title': 'Создание услуги',
		'button_text': 'Создать'
	})


@login_required
@staff_required
def service_edit(request, service_id):
	service = get_object_or_404(ServiceType, id=service_id)

	if request.method == 'POST':
		form = ServiceTypeForm(request.POST, instance=service)
		if form.is_valid():
			form.save()
			messages.success(request, f'Услуга "{service.name}" успешно обновлена')
			return redirect('service_types')
	else:
		form = ServiceTypeForm(instance=service)

	return render(request, 'services/service_form.html', {
		'form': form,
		'service': service,
		'title': 'Редактирование услуги',
		'button_text': 'Сохранить'
	})


@login_required
@staff_required
def service_delete(request, service_id):
	service = get_object_or_404(ServiceType, id=service_id)

	if request.method == 'POST':
		service_name = service.name
		service.delete()
		messages.success(request, f'Услуга "{service_name}" успешно удалена')
		return redirect('service_types')

	return render(request, 'services/service_confirm_delete.html', {
		'service': service
	})
