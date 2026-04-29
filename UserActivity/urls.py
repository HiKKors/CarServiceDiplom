from django.urls import path
from .views import (
    UserGarageVeiw, CustomLogoutView,
    UserBookingsView, Profile, ClientAbandonBookingsView, EditBookingView, CarServiceHistory, CarDeleteView, CarUpdateView, CarCreateView,
    complete_booking_and_pay, start_booking
)

urlpatterns = [
    path('garage/', UserGarageVeiw.as_view(), name='garage'),
    path('garage/add-car/', CarCreateView.as_view(), name='add_car'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('my-bookings/', UserBookingsView.as_view(), name='my_bookings'),
    path('profile/<int:pk>', Profile.as_view(), name='profile'),
    path('my-bookings/abandon_booking/<int:pk>', ClientAbandonBookingsView.as_view(), name='abandon_booking'),
    path('my-bookings/edit-booking/<int:pk>', EditBookingView.as_view(), name='edit_booking'),
    path('garage/car-service-history/<str:vin>', CarServiceHistory.as_view(), name='car_service_history'),
    path('garage/edit/<str:vin>/', CarUpdateView.as_view(), name='edit_car'),
    path('garage/delete/<str:vin>/', CarDeleteView.as_view(), name='delete_car'),
    path('booking/<int:booking_id>/complete/', complete_booking_and_pay, name='complete_booking'),
    path('booking/<int:booking_id>/start/', start_booking, name='start_booking'),
]