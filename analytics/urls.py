from django.urls import path
from .views import add_expense_view, DashboardView

urlpatterns = [
    path('dashboard/<int:service_id>', DashboardView.as_view(), name='dashboard'),
    path('dashboard/<int:service_id>/add-expense', add_expense_view, name='add_expense'),
]