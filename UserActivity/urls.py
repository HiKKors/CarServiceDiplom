from django.urls import path
from .views import (
    UserGarageVeiw, CustomLogoutView,
    UserBookingsView, Profile, add_user_car,
)

urlpatterns = [
    path('garage/', UserGarageVeiw.as_view(), name='garage'),
    path('add-car/', add_user_car, name='add_car'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('my-bookings/', UserBookingsView.as_view(), name='my_bookings'),
    path('profile/<int:pk>', Profile.as_view(), name='profile'),
    
    

]