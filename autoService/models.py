from datetime import datetime, timedelta, timezone, time
from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from accounts.models import Client

# REASONS = [
#     (1, 'Ремонтные работы')
#     (2, 'Проблемы с оборудованием'),
#     (3, 'Другое')
# ]


class WeekDays(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class AutoService(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(to='accounts.Client', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    address = models.CharField(max_length=100)
    workingHours = models.CharField(max_length=100)
    workingDays = models.ManyToManyField(WeekDays, related_name='working_days')
    
    def __str__(self):
        return f'{self.name}'
    
    def get_working_hours(self):
        start = int(self.workingHours.split('-')[0])
        end = int(self.workingHours.split('-')[1])
        slots = []
        for i in range(start, end):
            slots.append(f'{i:02d}:00')
            
        return slots
    
    def get_availability_for_date(self, target_date):
        boxes = self.box_set.all()
        time_slots = self.get_working_hours()
        table = {box.id: {slot: 'free' for slot in time_slots} for box in boxes}
        
        bookings = Booking.objects.filter(date = target_date).select_related('box')
        
        for book in bookings:
            for slot in time_slots:
                slot_hour = int(slot.split(':')[0])
                slot_start = time(slot_hour, 0)
                print(f'{slot_start} + {timezone}')
                slot_end = time((slot_hour + 1) % 24, 0)
                
                if book.start_time < slot_end and book.end_time > slot_start:
                    table[book.box_id][slot] = 'busy'
        
        return {
            'boxes': boxes,
            'time_slots': time_slots,
            'table': table,
        }
        
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
    
    # reason_is_closed = models.CharField(_('reason_type'), choices=REASONS, max_length=256, blank=True)
    
    def __str__(self):
        return f'Сервис {self.service_id} | {self.name}'
    

class Booking(models.Model):
    id = models.AutoField(primary_key=True)
    service_id = models.ForeignKey(to='AutoService', on_delete=models.CASCADE)
    user_id = models.ForeignKey(to='accounts.Client', on_delete=models.CASCADE)
    # user_car_id = models.ForeignKey(to='user.UserCar', on_delete=models.CASCADE, null=True, blank=True)
    date = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    equipment = models.ManyToManyField(to='Equipment', through='BookingEquipment')
    
    box = models.ForeignKey(to='Box', on_delete=models.CASCADE)
    
    comment = models.TextField(max_length=500)
    total_price = models.IntegerField(default=0)  
    
    class BookStatus(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        ACTIVE = 'active', 'Активная'
        COMPLETED = 'completed', 'Завершена'
        MISSED = 'missed', 'Пропущена'
    
    status = models.CharField(max_length=20, choices=BookStatus.choices, default=BookStatus.PENDING)
    
    arrived_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    has_penalty = models.BooleanField(default=False)
    
    def mark_arrived(self):
        now = datetime.now()
        book_date = datetime.strptime(self.date, "%Y-%m-%d").date()
        start_dt = datetime.combine(book_date, self.start_time)
        print(now)
        print('разница во времени', start_dt - timedelta(minutes=15))
        
        if now < start_dt - timedelta(minutes=15):
            raise ValidationError(
                "Слишком рано: можно отметить прибытие за 15 минут до начала"
            )

        if now > start_dt + timedelta(minutes=30): 
            self.has_penalty = True
            self.status = self.BookStatus.MISSED
        else:
            self.status = self.BookStatus.ACTIVE
            self.arrived_at = now

        self.save()
    
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
    