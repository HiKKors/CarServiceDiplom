from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.hashers import make_password

from django.contrib.auth.models import BaseUserManager

from django.utils.timezone import now

class ClientManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)  # если нужно

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
    
    
    
class Client(AbstractUser):
    username = None
    
    name = models.CharField(max_length=64, default='noname')
    surname = models.CharField(max_length=64, default='nosurname')
    email = models.EmailField(unique=True)  # Делаем email уникальным
    phone_number = models.CharField(max_length=11, unique=True, null=True)
    is_admin = models.BooleanField(default=False)
    
    objects = ClientManager()
    
    USERNAME_FIELD = 'email'  # Используем email для аутентификации
    
    REQUIRED_FIELDS = []
    
    
    def __str__(self):
        return self.email
       
    
# class ServiceAdmin(AbstractBaseUser, PermissionsMixin):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=64)
#     surname = models.CharField(max_length=64)
#     email = models.CharField(max_length=64)
#     password = models.CharField(max_length=64)
#     is_admin = models.BooleanField(default=True)
#     last_login = models.DateTimeField(null=True)
#     is_superuser = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
    
#     objects = ClientManager()
    
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     def __str__(self):
#         return self.email

#     @property
#     def is_staff(self):
#         """
#         Определяет, является ли пользователь частью административного персонала.
#         """
#         return self.is_admin