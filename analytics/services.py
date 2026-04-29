import json

from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import ExtractHour

from autoService.models import Booking
from .models import Expenses

class DashboardService:
    def __init__(self, service_id, days=7):
        self.service_obj = service_id
        self.start_date = timezone.now().date() - timedelta(days=days)
        
        
        self.base_bookings = Booking.objects.filter(service_id=service_id, date__gte = self.start_date, status='completed')
        
        self.base_expenses = Expenses.objects.filter(
            service=service_id, 
            date__gte=self.start_date
        )
        
    def get_financial_metrics(self):
        revenue = self.base_bookings.aggregate(Sum('total_price'))['total_price__sum'] or 0
        expenses = self.base_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        profit = revenue - expenses
        
        total_bookings = self.base_bookings.count()
        
        # средний чек
        avg_check = round(revenue / total_bookings, 2) if total_bookings > 0 else 0
        
        return {
            'revenue': float(revenue),
            'expenses': float(expenses),
            'profit': float(profit),
            'avg_check': float(avg_check),
            'total_bookings': total_bookings
        }
        
        # данные для графика выручки 
    def get_revenue_chart_data(self):
        daily_data = (
            self.base_bookings
            .values('date')
            .annotate(total=Sum('total_price'))
            .order_by('date')
        )
        
        return {
            'labels': [d['date'].strftime('%d.%m') for d in daily_data],
            'values': [float(d['total']) for d in daily_data]
        }
        
    def get_box_popularity_data(self):
    
        box_data = (
            self.base_bookings
            .values('box__name') # Предполагаю, что у модели Box есть поле name
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        return {
            'labels': [b['box__name'] for b in box_data],
            'values': [b['count'] for b in box_data]
        }
    
    def get_peak_hours_data(self):
        hourly_data = (
            self.base_bookings
            .annotate(hour=ExtractHour('start_time'))
            .values('hour')
            .annotate(count=Count('id'))
            .order_by('hour')
        )

        # Заполняем массив от 0 до 23, чтобы на графике не было "дыр", если в какой-то час нет записей
        hours = {str(i): 0 for i in range(8, 23)} # Предполагаем рабочее время с 8 до 22
        for data in hourly_data:
            hour_str = str(data['hour'])
            if hour_str in hours:
                hours[hour_str] = data['count']

        return {
            'labels': [f"{h}:00" for h in hours.keys()],
            'values': list(hours.values())
        }

    def get_full_dashboard_context(self):
        """Собирает все данные в один словарь для передачи в шаблон или сериализатор."""
        metrics = self.get_financial_metrics()
        
        return {
            'metrics': metrics,
            'charts': {
                'revenue': self.get_revenue_chart_data(),
                'boxes': self.get_box_popularity_data(),
                'peak_hours': self.get_peak_hours_data(),
            },
            'recent_bookings': self.base_bookings.order_by('-id')[:5]
        }
        
        
        
        
        
        
        
        
