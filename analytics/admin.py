from django.contrib import admin
from .models import Expenses, ExpensesCategory

# Register your models here.
admin.site.register(ExpensesCategory)
admin.site.register(Expenses)
