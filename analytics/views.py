from django.shortcuts import render, redirect

from django.shortcuts import get_object_or_404
from django.views import View

from .forms import AddExpenseForm
from autoService.models import AutoService

# Create your views here.
def add_expense_view(request, service):
    if request.method == "POST":
        form = AddExpenseForm(request.POST)
        if form.is_valid():
            service_id = get_object_or_404(AutoService, id=service).id
            expense = form.save()
            expense.service = service_id
            return redirect('dashboard')
    else:
        form = AddExpenseForm()
        return render(request, 'expenses_managment.html', {'form': form})
    
class DashboardView(View):
    pass