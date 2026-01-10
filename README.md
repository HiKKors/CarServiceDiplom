<h1>Дипломная работа на тему "Информационная система для онлайн-бронирования услуг и администрирования автосервисов самообслуживания"</h1>
Веб-приложение нацеленное на управление автосервисом, его боксами, оборудованием и бронированиями, позволяет получать детализированные отчеты о деятельности автосервиса. Клиентам дает возможность удобно и быстро забронировать место в боксе и оборудование, так же помогает отслеживать обслуживание своего автомобиля

<h1>Структура проекта</h1>
```bash
C:.
│   .env
│   .gitignore
│   city.csv
│   manage.py
│
├───accounts
│   │   admin.py
│   │   apps.py
│   │   backends.py
│   │   forms.py
│   │   models.py
│   │   tests.py
│   │   urls.py
│   │   views.py
│   │   __init__.py
│   │
│   ├───migrations
│   │   │   0001_initial.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           0001_initial.cpython-313.pyc
│   │           __init__.cpython-313.pyc
│   │
│   ├───templates
│   │   └───accounts
│   │           admin_login.html
│   │           admin_register.html
│   │           client_login.html
│   │           client_register.html
│   │           role_select.html
│   │
│   └───__pycache__
│           admin.cpython-313.pyc
│           apps.cpython-313.pyc
│           forms.cpython-313.pyc
│           models.cpython-313.pyc
│           urls.cpython-313.pyc
│           views.cpython-313.pyc
│           __init__.cpython-313.pyc
│
├───autoService
│   │   admin.py
│   │   apps.py
│   │   client_views.py
│   │   filters.py
│   │   forms.py
│   │   models.py
│   │   owner_views.py
│   │   tests.py
│   │   urls.py
│   │   __init__.py
│   │
│   ├───migrations
│   │   │   0001_initial.py
│   │   │   0002_sparepart_bookingsparepart_bookingdetail_parts.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           0001_initial.cpython-313.pyc
│   │           0002_sparepart_bookingsparepart_bookingdetail_parts.cpython-313.pyc
│   │           __init__.cpython-313.pyc
│   │
│   ├───templates
│   │   └───autoService
│   │           all_services.html
│   │           menu-layout.html
│   │
│   └───__pycache__
│           admin.cpython-313.pyc
│           apps.cpython-313.pyc
│           client_views.cpython-313.pyc
│           filters.cpython-313.pyc
│           forms.cpython-313.pyc
│           models.cpython-313.pyc
│           owner_views.cpython-313.pyc
│           urls.cpython-313.pyc
│           views.cpython-313.pyc
│           __init__.cpython-313.pyc
│
├───CarServiceDiplom
│   │   asgi.py
│   │   settings.py
│   │   urls.py
│   │   wsgi.py
│   │   __init__.py
│   │
│   └───__pycache__
│           settings.cpython-313.pyc
│           urls.cpython-313.pyc
│           wsgi.cpython-313.pyc
│           __init__.cpython-313.pyc
│
├───static
│   └───css
│       │   add_service.css
│       │   add_user_car.css
│       │   all_bookings.css
│       │   all_services.css
│       │   client_bookings.css
│       │   create_booking.css
│       │   default.css
│       │   edit_autoservice.css
│       │   garage.css
│       │   jquery.autocomplete.css
│       │   login.css
│       │   menu.css
│       │   profile.css
│       │   service_detail.css
│       │
│       └───css
│               add_service.css
│               add_user_car.css
│               all_bookings.css
│               all_services.css
│               client_bookings.css
│               create_booking.css
│               default.css
│               edit_autoservice.css
│               garage.css
│               jquery.autocomplete.css
│               login.css
│               menu.css
│               profile.css
│               service_detail.css
│
└───UserActivity
    │   admin.py
    │   apps.py
    │   forms.py
    │   models.py
    │   tests.py
    │   urls.py
    │   views.py
    │   __init__.py
    │
    ├───migrations
    │   │   0001_initial.py
    │   │   __init__.py
    │   │
    │   └───__pycache__
    │           0001_initial.cpython-313.pyc
    │           __init__.cpython-313.pyc
    │
    ├───templates
    │   └───UserActivity
    │           add-user-car.html
    │           booking_managment.html
    │           client-bookings.html
    │           equipment_check.html
    │           garage.html
    │           profile.html
    │
    └───__pycache__
            admin.cpython-313.pyc
            apps.cpython-313.pyc
            forms.cpython-313.pyc
            models.cpython-313.pyc
            urls.cpython-313.pyc
            views.cpython-313.pyc
            __init__.cpython-313.pyc
```
