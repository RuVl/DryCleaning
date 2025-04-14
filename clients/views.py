from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import ClientProfileForm


@login_required
def create_client_profile(request):
	if hasattr(request.user, 'client'):
		return redirect('client_dashboard')  # Уже есть профиль

	if request.method == 'POST':
		form = ClientProfileForm(request.POST)
		if form.is_valid():
			client = form.save(commit=False)
			client.user = request.user
			client.save()
			return redirect('client_dashboard')
	else:
		form = ClientProfileForm()

	return render(request, 'clients/create_profile.html', {'form': form})
