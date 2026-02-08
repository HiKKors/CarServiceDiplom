from django.contrib import admin
from .models import Expenses, ExpensesCategory, Incomes

# Register your models here.
admin.site.register(ExpensesCategory)
admin.site.register(Expenses)
admin.site.register(Incomes)
