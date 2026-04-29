from datetime import datetime, timedelta, timezone, time
from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from accounts.models import Client

from django.utils import timezone

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
        boxes = self.box_set.filter(is_opened=True)
        time_slots = self.get_working_hours()
        table = {box.id: {slot: 'free' for slot in time_slots} for box in boxes}
        
        bookings = Booking.objects.filter(date = target_date).select_related('box')
        
        for book in bookings:
            for slot in time_slots:
                slot_hour = int(slot.split(':')[0])
                slot_start = time(slot_hour, 0)
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
    
    is_available = models.BooleanField(default=True, verbose_name="Доступно для аренды")
    
    def __str__(self):
        status = "" if self.is_available else " [В ремонте]"
        return f'{self.name} {self.price} руб./час{status}'
    
class Box(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.IntegerField()
    service_id = models.ForeignKey(to='AutoService', on_delete=models.CASCADE)
    is_opened = models.BooleanField(default=True)
    
    @property
    def current_booking(self):
        """Возвращает текущую активную сессию в боксе (если есть)"""
        return self.booking_set.filter(status='active').first()

    @property
    def is_occupied(self):
        """Возвращает True, если в боксе прямо сейчас кто-то чинится"""
        return self.current_booking is not None
    
    def __str__(self):
        return f'Сервис {self.service_id} | {self.name}'
    
    
class RepairCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    
    is_oil_change = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория ремонта"
        verbose_name_plural = "Категории ремонта"
        
class Booking(models.Model):
    class BookStatus(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        ACTIVE = 'active', 'Активная'
        COMPLETED = 'completed', 'Завершена'
        MISSED = 'missed', 'Пропущена'
    
    id = models.AutoField(primary_key=True)
    service_id = models.ForeignKey(to='AutoService', on_delete=models.CASCADE)
    user_id = models.ForeignKey(to='accounts.Client', on_delete=models.CASCADE)
    user_car = models.ForeignKey(to='UserActivity.UserCar', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(verbose_name='Дата')
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    equipment = models.ManyToManyField(to='Equipment', through='BookingEquipment')
    
    box = models.ForeignKey(to='Box', on_delete=models.CASCADE)
    
    repair_category = models.ForeignKey(
        RepairCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Категория работ"
    )
    
    total_price = models.IntegerField(default=0)  
    
    payment_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="ID платежа ЮKassa")
    arrived_at = models.DateTimeField(null=True, blank=True, verbose_name="Время заезда")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Время выезда")
    has_penalty = models.BooleanField(default=False, verbose_name="Штраф за опоздание")
    extra_time_minutes = models.PositiveIntegerField(default=0, verbose_name="Перерасход времени (мин)")
    
    
    status = models.CharField(max_length=20, choices=BookStatus.choices, default=BookStatus.PENDING)
    
    def start_session(self):
        """Логика НАЧАЛА обслуживания"""
        now = timezone.localtime()
        start_dt = timezone.make_aware(datetime.combine(self.date, self.start_time))
        
        # 1. Слишком рано (больше чем за 15 минут)
        if now < (start_dt - timedelta(minutes=15)):
            raise ValidationError("Слишком рано. Бокс еще не готов.")
            
        # 2. Опоздание (прошло больше 30 минут от старта)
        if now > (start_dt + timedelta(minutes=30)):
            self.status = self.BookStatus.MISSED
            self.has_penalty = True
            self.save()
            # Освобождаем бокс (сработает через сигналы или просто статус)
            raise ValidationError("Вы опоздали более чем на 30 минут. Бронь аннулирована.")
            
        # 3. Успешный старт
        self.status = self.BookStatus.ACTIVE
        self.arrived_at = now
        self.save()

    def complete_session(self, mileage_data=None):
        """Логика ЗАВЕРШЕНИЯ обслуживания"""
        if self.status != self.BookStatus.ACTIVE:
            raise ValidationError("Нельзя завершить бронь, которая не была начата.")

        now = timezone.now()
        end_dt = timezone.make_aware(datetime.combine(self.date, self.end_time))
        
        self.status = self.BookStatus.COMPLETED
        self.completed_at = now
        self.save()
        
        # Проверка на перерасход времени (Overstay)
        # Если клиент просидел дольше, чем планировал (дадим 10 минут грейс-периода)
        if now > (end_dt + timedelta(minutes=10)):
            extra_time = now - end_dt
            extra_minutes = int(extra_time.total_seconds() / 60)
            # Здесь можно генерировать доп. счет, но пока просто логируем
            print(f"Клиент {self.user_id} пересидел на {extra_minutes} минут.")
            
        # Обновление пробега, если он передан
        if mileage_data and self.user_car:
            # Получаем или создаем детали брони
            from autoService.models import BookingDetail # Локальный импорт во избежание circular import
            booking_detail, _ = BookingDetail.objects.get_or_create(booking=self)
            booking_detail.mileage = mileage_data
            booking_detail.save()
        
    def can_edit_or_delete(self):
        # Берем правильное текущее время с учетом часового пояса проекта
        now = datetime.now()
        
        book_date = datetime.strptime(self.date, "%Y-%m-%d").date()
        start_dt = datetime.combine(book_date, self.start_time)
        
        # Возвращаем результат сравнения напрямую
        return now < (start_dt - timedelta(hours=12))
    
    @property
    def cancellation_info(self):
        """
        Возвращает словарь с информацией о правилах отмены/изменения.
        """
        # Склеиваем дату и время в один объект datetime с учетом часового пояса
        # (Предполагается, что у тебя есть поля date и start_time)
        booking_datetime = timezone.make_aware(
            datetime.datetime.combine(self.date, self.start_time)
        )
        
        now = timezone.now()
        time_difference = booking_datetime - now
        hours_left = time_difference.total_seconds() / 3600

        # Если время уже прошло
        if hours_left <= 0:
            return {
                'is_past': True,
                'is_free': False,
                'fee': 0,
            }
            
        # Если осталось больше или ровно 12 часов (Бесплатно)
        if hours_left >= 12:
            return {
                'is_past': False,
                'is_free': True,
                'fee': 0,
            }
            
        # Если осталось МЕНЬШЕ 12 часов (Платно!)
        return {
            'is_past': False,
            'is_free': False,
            'fee': 500, # Укажи здесь сумму штрафа (руб.)
        }
        
    @property
    def can_be_started(self):
        """Можно ли нажать кнопку 'Начать' прямо сейчас"""
        now = timezone.now()
        # Кнопка активна за 10 минут до начала и только если статус 'pending'
        start_dt = timezone.make_aware(datetime.combine(self.date, self.start_time))
        return self.status == 'pending' and now >= (start_dt - timedelta(minutes=10))

    @property
    def wait_time_display(self):
        """Сколько минут осталось до возможности нажать кнопку"""
        now = timezone.now()
        start_dt = timezone.make_aware(datetime.combine(self.date, self.start_time))
        wait_time = (start_dt - timedelta(minutes=10)) - now
        if wait_time.total_seconds() > 0:
            return int(wait_time.total_seconds() // 60)
        return 0
    
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
    
class Staff(models.Model):
    specialist_id = models.AutoField(primary_key=True)
    service = models.ForeignKey(to='AutoService', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    surname = models.CharField(max_length=100, null=False, blank=False)
    salary = models.IntegerField(default=0)
