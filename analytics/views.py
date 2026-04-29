from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.shortcuts import get_object_or_404
from django.views import View
from django.db.models import Sum, Count

from datetime import datetime, timedelta

from openpyxl import Workbook

from analytics.services import DashboardService

from .forms import AddExpenseForm
from autoService.models import AutoService, Booking

from .models import Expenses

import json

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
    service_obj = get_object_or_404(AutoService, id=service)
    
    # период, по дефолту 7 дней
    days = int(request.GET.get('days', 7))
    
    analytics_service = DashboardService(service, days=days)
    
    dashboard_data = analytics_service.get_full_dashboard_context()
    
    metrics_layout = [
        ('Выручка', dashboard_data['metrics']['revenue'], 'fa-wallet', 'primary'),
        ('Расходы', dashboard_data['metrics']['expenses'], 'fa-credit-card', 'danger'),
        ('Прибыль', dashboard_data['metrics']['profit'], 'fa-chart-line', 'success'),
        ('Средний чек', dashboard_data['metrics']['avg_check'], 'fa-hand-holding-usd', 'info'),
    ]
    

    
    context = {
        'service': service_obj,
        'metrics': dashboard_data['metrics'],
        'recent_bookings': dashboard_data['recent_bookings'],
        'charts_json': json.dumps(dashboard_data['charts']),
        'metrics_layout': metrics_layout
    }
    
    return render(request=request, template_name='analytics/analytics_dashboard.html', context=context)

def get_service_mounth_report_view(request, service):
    print('REPORT')
    print(service)
    response = HttpResponse(content_type='application/ms-excel; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
    
    wb = Workbook()
    ws = wb.active
    ws.title = 'AutoService'
    
    headers = ['Name', 'count']
    ws.append(headers)
    
    service = AutoService.objects.get(id=service)
    bookings = Booking.objects.filter(service_id = service).count()
    print('count', bookings)
    
    ws.append([service.name, bookings])
    
    wb.save(response)
    return response