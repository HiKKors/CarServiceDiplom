from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(AutoService)
admin.site.register(Box)
admin.site.register(Equipment)
admin.site.register(Booking)
admin.site.register(SparePart)
admin.site.register(BookingDetail)
admin.site.register(BookingSparePart)