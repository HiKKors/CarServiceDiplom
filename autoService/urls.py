from django.urls import path

from .client_views import (AllServicesList, ServiceDetail, BookingManagment, PendingBookings, 
    mark_completed, get_boxes, get_available_times, add_review, create_booking, add_booking_detail, mark_arrived)

from .owner_views import (MyServicesView, MyServiceManagmentView, EditAutoServiceView, AllBookingsView, MyStaffView, MyServicesForStaffView, 
    add_staff_view, add_auto_service, toggle_box_status, toggle_equipment_status)

urlpatterns = [
    # CLIENT URLS
    path('', AllServicesList.as_view(), name='main'),
    path('service-info/<int:pk>', ServiceDetail.as_view(), name='service'),
    path('create-booking/<int:service_id>', create_booking, name='create_booking'),
    path('create-booking/<int:service_id>/add_booking_detail/<int:booking_id>', add_booking_detail, name='add_booking_detail'),
    path('booking_managment/<int:pk>', BookingManagment.as_view(), name='booking_managment'),
    path('mark_arrived/<int:booking_id>', mark_arrived, name='mark_arrived'),
    path('mark_completed/<int:booking_id>', mark_completed, name='mark_completed'),
    path('pending_bookings/', PendingBookings.as_view(), name='pending_bookings'),
    path('service-info/<int:service_id>/add-review', add_review, name='add_review'),
    
    #test booking
    path('api/boxes/', get_boxes, name='api_boxes'),
    path('api/available-times/', get_available_times, name='api_available_times'),
    
    # ADMIN URLS
    path('service-admin/create-autoservice/', add_auto_service, name='create_autoservice'),
    path('service-admin/my-services/', MyServicesView.as_view(), name='my_services'),
    path('service-admin/my-services/managment/<int:pk>', MyServiceManagmentView.as_view(), name = 'my_service_managment'),
    path('service-admin/my-services/managment/<int:pk>/edit', EditAutoServiceView.as_view(), name='edit_autoservice'),
    path('service-admin/all-bookings/', AllBookingsView.as_view(), name='all_bookings'),
    path('service-admin/services_staff/', MyServicesForStaffView.as_view(), name='services_staff'),
    path('service-admin/services_staff/<int:service_id>', MyStaffView.as_view(), name='my_staff'),
    path('service-admin/services_staff/<int:service>/add', add_staff_view, name='add_staff'),
    path('box/<int:box_id>/toggle/', toggle_box_status, name='toggle_box_status'),
    path('equipment/<int:equipment_id>/toggle/', toggle_equipment_status, name='toggle_equipment_status'),
]