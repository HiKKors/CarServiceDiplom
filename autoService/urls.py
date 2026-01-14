from django.urls import path

from .client_views import AllServicesList, ServiceDetail, create_booking, add_booking_detail, mark_arrived, BookingManagment, PendingBookings
from .owner_views import MyServicesView, MyServiceManagmentView, EditAutoServiceView, get_service_mounth_report_view, AllBookingsView, add_auto_service

urlpatterns = [
    # CLIENT URLS
    path('', AllServicesList.as_view(), name='main'),
    path('service-info/<int:pk>', ServiceDetail.as_view(), name='service'),
    path('create-booking/<int:service_id>', create_booking, name='create_booking'),
    path('create-booking/<int:service_id>/add_booking_detail/<int:booking_id>', add_booking_detail, name='add_booking_detail'),
    path('booking_managment/<int:pk>', BookingManagment.as_view(), name='booking_managment'),
    path('mark_arrived/<int:booking_id>', mark_arrived, name='mark_arrived'),
    path('pending_bookings/', PendingBookings.as_view(), name='pending_bookings'),
    
    # ADMIN URLS
    path('service-admin/create-autoservice/', add_auto_service, name='create_autoservice'),
    path('service-admin/my-services/', MyServicesView.as_view(), name='my_services'),
    path('service-admin/my-services/managment/<int:pk>', MyServiceManagmentView.as_view(), name = 'my_service_managment'),
    path('service-admin/my-services/managment/<int:pk>/edit', EditAutoServiceView.as_view(), name='edit_autoservice'),
    path('service-admin/my-services/create-report/<int:service_id>', get_service_mounth_report_view, name='service-report'),
    path('service-admin/all-bookings/', AllBookingsView.as_view(), name='all_bookings'),
]