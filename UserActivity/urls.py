from django.urls import path
from .views import (
    UserGarageVeiw, CustomLogoutView, AllBookingsView,
    UserBookingsView, Profile, MyServicesView, MyServiceManagmentView, EditAutoServiceView,
    add_auto_service, add_user_car, get_service_mounth_report_view
)

urlpatterns = [
    path('service-admin/create-autoservice/', add_auto_service, name='create_autoservice'),
    path('garage/', UserGarageVeiw.as_view(), name='garage'),
    path('add-car/', add_user_car, name='add_car'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('my-bookings/', UserBookingsView.as_view(), name='my_bookings'),
    path('profile/<int:pk>', Profile.as_view(), name='profile'),
    
    path('service-admin/my-services/', MyServicesView.as_view(), name='my_services'),
    path('service-admin/my-services/managment/<int:pk>', MyServiceManagmentView.as_view(), name = 'my_service_managment'),
    path('service-admin/my-services/managment/<int:pk>/edit', EditAutoServiceView.as_view(), name='edit_autoservice'),
    path('service-admin/my-services/create-report/<int:service_id>', get_service_mounth_report_view, name='service-report'),
    path('service-admin/all-bookings/', AllBookingsView.as_view(), name='all_bookings'),

]