from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import login

from django.views import View

from django.views.generic.base import TemplateView

from .forms import ClientLoginForm, ClientRegisterForm
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create your views here.
class ClientLoginView(LoginView):
    logger.info('ClientLoginView')
    template_name = 'accounts/client_login.html'
    form_class = ClientLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        logger.info(f'пользователь успешно вошел в систему, email {self.request.user.email}')
        messages.success(self.request, 'Вы успешно вошли в систему!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print(form)
        logger.info('FORM INVALID')
        messages.error(self.request, 'Неверный email или пароль. Попробуйте снова.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        user = self.request.user
        if user.is_admin:
            logger.info(f'Авторизация администратора, email: {user.email}')
            return reverse_lazy('my_services')
        elif not user.is_admin:
            logger.info(f'Авторизация клиента, email: {user.email}')
            return reverse_lazy('main')
    
# class ServiceAdminLoginView(LoginView):
#     template_name = 'accounts/admin_login.html'
#     form_class = ServiceAdminLoginForm
#     redirect_authenticated_user = True
    
#     def form_valid(self, form):
#         admin = form.get_user()
#         admin.backend = 'user.backends.ClientAuthenticationBackend'
#         login(self.request, admin)
        
#         messages.success(self.request, 'Вы успешно вошли в систему!')
#         return super().form_valid(form)
    
#     def form_invalid(self, form):
#         messages.error(self.request, 'Неверный email или пароль. Попробуйте снова.')
#         return super().form_invalid(form)
    
#     def get_success_url(self):
#         return reverse_lazy('my_services')


def client_register_view(request):
    logger.info('ClientRegister')
    
    role = request.GET.get('role', 'client')
    
    print(role)
    if request.method == 'POST':        
        logger.info('Регистрация POST')
        form = ClientRegisterForm(request.POST)
        role = request.POST.get('role', 'client')
        print(f'ROLE POST {role}')
        if form.is_valid():
            client = form.save(commit=False)
            client.is_admin = (role == 'admin')
            client.set_password(form.cleaned_data['password1'])
            client.save()
            
            # указываем кастомный бэк для авторизации
            # client.backend = 'user.backends.ClientAuthenticationBackend'
            
            # авторизация после регистрации
            login(request, client)
            messages.success(request=request, message='Вы успешно зарегистрировались!')
            if role == 'admin':
                return redirect('my_services') 
            if role == 'client':
                return redirect('main')
        else:
            logger.warning('Ошибка регистрации')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ClientRegisterForm()
        
    return render(request, 'accounts/client_register.html', {'form': form, 'role': role})

# def service_admin_register_view(request):
#     if request.method == 'POST':
#         form = ServiceAdminRegisterForm(request.POST)
#         if form.is_valid():
#             service_admin = form.save(commit = False)
#             service_admin.set_password(form.cleaned_data['password1'])
#             service_admin.save()
            
#             service_admin.backend = 'user.backends.ServiceAdminAuthenticationBackend'
            
#             # login(request, service_admin)
            
#             messages.success(request=request, message='Вы успешно зарегистрировались!')
#             return redirect('my_services')
#         else:
#             messages.error(request, 'Ошибка регистрации')
#     else:
#         form = ClientRegisterForm()
        
#     return render(request, 'accounts/admin_register.html', {'form': form})

class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    
def role_select_view(request):
    return render(request, 'accounts/role_select.html')