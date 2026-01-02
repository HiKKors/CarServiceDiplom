from django.db import models
from django.utils.translation import gettext_lazy as _

REASONS = [
    (1, 'Ремонтные работы')
    (2, 'Проблемы с оборудованием'),
    (3, 'Другое')
]


class WeekDays(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class AutoService(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.ForeignKey(to='accounts.ServiceAdmin', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    address = models.CharField(max_length=100)
    workingHours = models.CharField(max_length=100)
    workingDays = models.ManyToManyField(WeekDays, related_name='working_days')
    
    def __str__(self):
        return f'{self.name}'
    
class Equipment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    service_id = models.ForeignKey(to='AutoService', on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.name} {self.price} руб./час'
    
class Box(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.IntegerField()
    service_id = models.ForeignKey(to='AutoService', on_delete=models.CASCADE)
    is_opened = models.BooleanField(default=True)
    
    reason_is_closed = models.CharField(_('reason_type'), choices=REASONS, max_length=256, blank=True)
    
    def __str__(self):
        return f'Сервис {self.service_id} | {self.name}'
    

class Booking(models.Model):
    id = models.AutoField(primary_key=True)
    service_id = models.ForeignKey(to='AutoService', on_delete=models.CASCADE)
    user_id = models.ForeignKey(to='accounts.Client', on_delete=models.CASCADE)
    user_car_id = models.ForeignKey(to='user.UserCar', on_delete=models.CASCADE)
    date = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    equipment = models.ManyToManyField(to='Equipment', through='BookingEquipment')
    
    box = models.ForeignKey(to='Box', on_delete=models.CASCADE)
    
    comment = models.TextField(max_length=500)
    total_price = models.IntegerField(default=0)    
    
    def __str__(self):
        return f'Сервис {self.service_id} | Клиент {self.user_id} | {self.date}'
    
class BookingDetail(models.Model):
    booking = models.ForeignKey(to="Booking", on_delete=models.CASCADE)
    mileage = models.IntegerField()
    planned_works = models.TextField() # предполагаемые работы
    parts = models.ManyToManyField(to='SparePart', through='BookingSparePart')
    
# используемые запчасти
class SparePart(models.Model):
    name = models.CharField(max_length=100)
    article = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f'{self.name} | {self.article}'
    
class BookingSparePart(models.Model):  #FORMSET
    booking_detail = models.ForeignKey(to='BookingDetail', on_delete=models.CASCADE)
    part = models.ForeignKey(to='SparePart', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
class BookingEquipment(models.Model):
    booking_id = models.ForeignKey(to='Booking', on_delete=models.CASCADE)
    equipment_id = models.ForeignKey(to='Equipment', on_delete=models.CASCADE)
    