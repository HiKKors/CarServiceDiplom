from django.db import models
from django.utils import timezone

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
    # Добавили title, который ты хотел использовать в шаблоне
    title = models.CharField(max_length=200, verbose_name='Название расхода', null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    
    # ИСПРАВЛЕНО: Теперь дата по умолчанию сегодняшняя, но ее можно менять в форме
    date = models.DateField(default=timezone.now, verbose_name='Дата')
    
    description = models.TextField(blank=True, verbose_name='Комментарий')

    def __str__(self):
        return f"{self.title} - {self.amount} ₽"