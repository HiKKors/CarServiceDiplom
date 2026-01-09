from django.db import models
    
class UserCar(models.Model):
    vin = models.CharField(primary_key=True, max_length=32)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    generation = models.CharField(max_length=50)
    year = models.IntegerField(default=0)
    engine_capacity = models.FloatField(default=0)
    power = models.IntegerField(default=0)
    
    user = models.ForeignKey(to='accounts.Client', on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.vin}'
    
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(to='accounts.Client', on_delete=models.CASCADE)
    service_id = models.ForeignKey(to='autoService.AutoService', on_delete=models.DO_NOTHING)
    
    mark = models.IntegerField(default=0)
    comment = models.TextField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(f'{self.date} {self.user}')
