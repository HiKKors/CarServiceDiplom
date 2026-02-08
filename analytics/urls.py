from django.urls import path
from .views import add_expense_view, dashboard_view

urlpatterns = [
    path('dashboard/<int:service>', dashboard_view, name='dashboard'),
    path('dashboard/<int:service>/add-expense', add_expense_view, name='add_expense'),
]