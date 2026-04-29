from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Client

class ClientLoginForm(AuthenticationForm):
    username = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'email-input',
        'placeholder': 'Введите ваш email',
        'id': 'email'
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'password-input',
        'placeholder': 'Введите ваш пароль',
        'id': 'password'
    }))
    
    class Meta:
        model = Client
        fields = ('username', 'password')

class ClientRegisterForm(UserCreationForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'name-input',
        'placeholder': 'Введите ваше имя',
        'id': 'name'
    }))
    surname = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'surname-input',
        'placeholder': 'Введите вашу фамилию',
        'id': 'surname'
    }))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'email-input',
        'placeholder': 'Введите ваш email',
        'id': 'email'
    }))
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'phone-input',
        'placeholder': 'Введите ваш номер телефона',
        'id': 'phone_number'
    }))
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'pass1-input',
        'placeholder': 'Придумайте пароль',
        'id': 'password1'
    }))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'pass2-input',
        'placeholder': 'Повторите пароль',
        'id': 'password2'
    }))
    
    class Meta:
        model = Client
        fields = ('name', 'surname', 'email', 'phone_number', 'password1', 'password2')


# class ServiceAdminLoginForm(AuthenticationForm):
#     username = forms.EmailField(required=True, widget=forms.TextInput(attrs={
#         'class': 'email-input',
#         'placeholder': 'Введите ваш email',
#         'id': 'email'
#     }))
    
#     password = forms.CharField(widget=forms.PasswordInput(attrs={
#         'class': 'password-input',
#         'placeholder': 'Введите ваш пароль',
#         'id': 'password'
#     }))
    
#     class Meta:
#         model = ServiceAdmin
#         fields = ('username', 'password')

# class ServiceAdminRegisterForm(UserCreationForm):
#     name = forms.CharField(required=True, widget=forms.TextInput(attrs={
#         'class': 'name-input',
#         'placeholder': 'Введите ваше имя',
#         'id': 'admin-name'
#     }))
#     surname = forms.CharField(required=True, widget=forms.TextInput(attrs={
#         'class': 'surname-input',
#         'placeholder': 'Введите вашу фамилию',
#         'id': 'admin-surname'
#     }))
#     email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
#         'class': 'email-input',
#         'placeholder': 'Введите ваш email',
#         'id': 'admin-email'
#     }))
#     password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
#         'class': 'pass1-input',
#         'placeholder': 'Придумайте пароль',
#         'id': 'admin-pass1'
#     }))
#     password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
#         'class': 'pass2-input',
#         'placeholder': 'Повторите пароль',
#         'id': 'admin-pass2'
#     }))
    
#     class Meta:
#         model = ServiceAdmin
#         fields = ('name', 'surname', 'email', 'password1', 'password2')