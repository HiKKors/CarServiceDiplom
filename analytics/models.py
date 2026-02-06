from django.db import models

# Create your models here.

class ExpensesCategory(models.Model):
    name = models.CharField(max_length=100)
    is_recurring = models.BooleanField(default=False)

class Expenses(models.Model):
    CATEGORY_CHOICES = [
        ('utility', 'Коммунальные услуги'),
        ('rent', 'Аренда'),
        ('supplies', 'Расходные материалы'),
        ('repair', 'Ремонт оборудования'),
        ('other', 'Прочее'),
    ]
    
    service = models.ForeignKey(to='autoService.AutoService', on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)

# для истории доходов
class Incomes(models.Model):
    service = models.ForeignKey(to='autoService.AutoService', on_delete=models.CASCADE)
    mounth_year = models.DateField()
    full_amount = models.DecimalField(max_digits=10, decimal_places=2)