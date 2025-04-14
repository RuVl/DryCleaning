# Create your views here.

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView

from accounts.decorators import staff_required
from .forms import BranchForm
from .models import Branch


class BranchListView(ListView):
	model = Branch
	template_name = 'branches/list.html'
	context_object_name = 'branches'

	def get_queryset(self):
		return Branch.objects.all().order_by('name')


class BranchDetailView(DetailView):
	model = Branch
	template_name = 'branches/detail.html'
	context_object_name = 'branch'


def branch_detail(request, branch_id):
	branch = get_object_or_404(Branch, id=branch_id)
	return render(request, 'branches/detail.html', {'branch': branch})


@login_required
@staff_required
def branch_create(request):
	if request.method == 'POST':
		form = BranchForm(request.POST, request.FILES)
		if form.is_valid():
			branch = form.save()
			messages.success(request, f'Филиал "{branch.name}" успешно создан')
			return redirect('branches')
	else:
		form = BranchForm()

	return render(request, 'branches/branch_form.html', {
		'form': form,
		'title': 'Создание филиала',
		'button_text': 'Создать'
	})


@login_required
@staff_required
def branch_edit(request, branch_id):
	branch = get_object_or_404(Branch, id=branch_id)

	if request.method == 'POST':
		form = BranchForm(request.POST, request.FILES, instance=branch)
		if form.is_valid():
			form.save()
			messages.success(request, f'Филиал "{branch.name}" успешно обновлен')
			return redirect('branches')
	else:
		form = BranchForm(instance=branch)

	return render(request, 'branches/branch_form.html', {
		'form': form,
		'branch': branch,
		'title': 'Редактирование филиала',
		'button_text': 'Сохранить'
	})


@login_required
@staff_required
def branch_delete(request, branch_id):
	branch = get_object_or_404(Branch, id=branch_id)

	if request.method == 'POST':
		branch_name = branch.name
		branch.delete()
		messages.success(request, f'Филиал "{branch_name}" успешно удален')
		return redirect('branches')

	return render(request, 'branches/branch_confirm_delete.html', {
		'branch': branch
	})
