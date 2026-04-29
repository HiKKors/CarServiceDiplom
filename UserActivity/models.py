from django.db import models
from autoService.models import BookingDetail
    
class UserCar(models.Model):
    vin = models.CharField(primary_key=True, max_length=32)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    generation = models.CharField(max_length=50)
    year = models.IntegerField(default=0)
    engine_capacity = models.FloatField(default=0)
    power = models.IntegerField(default=0)
    current_mileage = models.IntegerField(default=0)
    
    user = models.ForeignKey(to='accounts.Client', on_delete=models.CASCADE)
    
    
    @property
    def oil_status(self):
        """
        Возвращает данные о состоянии масла для вывода в Гараже
        """
        interval = 10000  # Интервал замены
        
        # 1. Ищем детали последней ЗАВЕРШЕННОЙ брони по замене масла
        last_oil_detail = BookingDetail.objects.filter(
            booking__user_car=self,
            booking__status='completed',           # Убедись, что статус у тебя пишется так
            booking__repair_category__is_oil_change=True, # Опираемся на галочку в категории
            mileage__isnull=False                  # Проверяем, что пробег был заполнен
        ).order_by('-booking__date', '-booking__start_time').first()
        
        print('last_oil_detail', last_oil_detail)

        if not last_oil_detail:
            return None  # Масло еще ни разу не меняли в нашем сервисе

        # 2. Ищем самый актуальный пробег (любая последняя завершенная запись)
        latest_detail = BookingDetail.objects.filter(
            booking__user_car=self,
            booking__status='completed',
            mileage__isnull=False
        ).order_by('-booking__date', '-booking__start_time').first()

        last_oil_mileage = last_oil_detail.mileage
        current_mileage = latest_detail.mileage if latest_detail else last_oil_mileage
        
        # 3. Считаем остаток
        driven_since_change = current_mileage - last_oil_mileage
        remaining_km = interval - driven_since_change
        
        # Небольшая защита: если перекатал масло, пусть остаток будет 0, а не минус
        if remaining_km < 0:
            remaining_km = 0

        # Считаем процент для красивого Progress Bar (не больше 100)
        percentage = min((driven_since_change / interval) * 100, 100)

        return {
            'last_changed_at': last_oil_mileage,
            'current_mileage': current_mileage,
            'remaining_km': remaining_km,
            'percentage': percentage,
            'needs_change': remaining_km <= 500  # Флаг "Пора менять" (осталось <= 500 км)
        }
    
    def __str__(self):
        return f'{self.make} {self.model} | {self.vin}'
    
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(to='accounts.Client', on_delete=models.CASCADE)
    service_id = models.ForeignKey(to='autoService.AutoService', on_delete=models.DO_NOTHING)
    
    mark = models.IntegerField(default=0)
    comment = models.TextField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(f'{self.date} {self.user}')
