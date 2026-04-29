from django.urls import path
from .views import ClientLoginView, client_register_view, role_select_view

urlpatterns = [
    path('register/', client_register_view, name='register'),
    path('login/', ClientLoginView.as_view(), name='login'),
    path('role_select/', role_select_view, name='role_select'),
    # path('admin_login/', ServiceAdminLoginView.as_view(), name='admin_login'),
    # path('admin_register/', service_admin_register_view, name='admin_register'),
]