from django.shortcuts import render, redirect

from django.shortcuts import get_object_or_404
from django.views import View
from django.db.models import Sum, Count

from datetime import datetime, timedelta

from .forms import AddExpenseForm
from autoService.models import AutoService, Booking

from .models import Expenses, Incomes

# Create your views here.
def add_expense_view(request, service):
    if request.method == "POST":
        form = AddExpenseForm(request.POST)
        if form.is_valid():
            service_id = get_object_or_404(AutoService, id=service)
            expense = form.save(commit=False)
            expense.service = service_id
            
            expense.save()
            return redirect('dashboard', service=service)
    else:
        form = AddExpenseForm()
        context = {
            'form': form,
            'service': service,
        }
        return render(request, 'analytics/expenses_managment.html', context=context)

def dashboard_view(request, service):
    total_expenses = Expenses.objects.aggregate(Sum('amount'))['amount__sum']
    total_incomes = Incomes.objects.aggregate(Count('id'))
    
    service_bookings = Booking.objects.filter(service_id = service)
    total_bookings = service_bookings.count()
    recent_bookings = service_bookings.order_by('id')[:5]
    
    last_week = datetime.now() - timedelta(days=7)
    daily_revenue = (
        Booking.objects.filter(date__gte=last_week, status='completed')
        .values('date')
        .order_by('date')
    )
    
    # Подготовка списков для JavaScript
    labels = [d['date'].strftime('%d.%m') for d in daily_revenue]
    values = [float(d['total']) for d in daily_revenue]

    context = {
        'total_expenses': total_expenses,
        'total_bookings': total_bookings,
        'labels': labels,
        'values': values,
        'recent_bookings': recent_bookings,
        'service': service,
    }
    return render(request, 'analytics/analytics_dashboard.html', context)