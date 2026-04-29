# from django.contrib.auth.hashers import check_password
# from .models import ServiceAdmin, Client

# from django.contrib.auth.backends import BaseBackend

# import logging

# logger = logging.getLogger('user')


# logger.info('Это тестовое сообщение для проверки логирования.')
        
        
# class ClientAuthenticationBackend(BaseBackend):
#     logger.info('Класс ClientAuthenticationBackend')
#     def authenticate(self, request, email=None, password=None, username = None):
#         print('AUTH DEF')
#         email = email or username
#         logger.info('Пытаемся авторизовать пользователя с email:')
#         try:
#             user = ServiceAdmin.objects.get(email=email)
#             logger.info(f'Нашел администратора с email: {email}')
#         except ServiceAdmin.DoesNotExist:
#             try:
#                 user = Client.objects.get(email=email)
#                 logger.info(f'Не нашел админа, но нашел клиента с email: {email}')
#             except Client.DoesNotExist:
#                 logger.warning(f'Не нашел никого с email: {email}')
#                 return None

#             # Проверяем пароль и активность пользователя
#         if user.check_password(password):
#             if user.is_active:
#                 logger.info(f"Успешная авторизация для полльзователя с email: {email}")
#                 return user
#             else:
#                 logger.warning(f"Пользователь с email: {email} не активен")
#         else:
#             logger.warning(f"Не правильный пароль для пользоватля с email: {email}")
#         return None

#     def get_user(self, user_id):
#         try:
#             return ServiceAdmin.objects.get(pk=user_id)
#         except ServiceAdmin.DoesNotExist:
#             try:
#                 return Client.objects.get(pk=user_id)
#             except Client.DoesNotExist:
#                 return None