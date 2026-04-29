
import uuid

from django.shortcuts import get_object_or_404, render, redirect, get_list_or_404
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.edit import UpdateView
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

from .models import UserCar, Review
from autoService.models import Booking, BookingDetail
from accounts.models import Client
from .forms import UserCarForm, EditBookingForm

import logging

from yookassa import Payment

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

class CarCreateView(CreateView):
    model = UserCar
    form_class = UserCarForm
    template_name = 'UserActivity/add_user_car.html' # Шаблон сделаем ниже
    success_url = reverse_lazy('garage') # Перенаправляем обратно в гараж

    def form_valid(self, form):
        # Привязываем машину к текущему пользователю перед сохранением
        # ЗАМЕНИ 'user' на то, как у тебя называется связь с клиентом в модели UserCar (например, 'user_id' или 'owner')
        form.instance.user = self.request.user 
        messages.success(self.request, 'Автомобиль успешно добавлен в гараж!')
        return super().form_valid(form)

# --- 2. РЕДАКТИРОВАНИЕ АВТО ---
class CarUpdateView(UpdateView):
    model = UserCar
    form_class = UserCarForm
    template_name = 'UserActivity/add_user_car.html'
    success_url = reverse_lazy('garage')
    
    # Ищем по VIN
    slug_field = 'vin'
    slug_url_kwarg = 'vin'

    def get_queryset(self):
        # Жесткая проверка: юзер может редактировать ТОЛЬКО свои машины
        return UserCar.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Данные автомобиля успешно обновлены!')
        return super().form_valid(form)
    

# --- 3. УДАЛЕНИЕ АВТО ---
class CarDeleteView(DeleteView):
    model = UserCar
    success_url = reverse_lazy('garage')
    
    # Ищем по VIN
    slug_field = 'vin'
    slug_url_kwarg = 'vin'

    def get_queryset(self):
        # Жесткая проверка: юзер может удалять ТОЛЬКО свои машины
        return UserCar.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Автомобиль удален из гаража.')
        return super().form_valid(form)

class UserGarageVeiw(ListView):
    queryset = UserCar.objects.all()
    template_name = 'UserActivity/garage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user_cars = UserCar.objects.filter(user=self.request.user.id)
        
        context['user_cars'] = user_cars    
        
        return context
    
class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    
class UserBookingsView(ListView):
    model = Booking
    template_name = 'UserActivity/client_bookings.html'
    
    now = timezone.now()
    print(now)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bookings = Booking.objects.filter(user_id=self.request.user)
        
        # 2. Возвращаем старую переменную, чтобы старый шаблон тоже работал!
        context['user_bookings'] = bookings
        
        # 3. Используем ТВОИ статусы из модели (BookStatus) вместо простого текста
        # Замени эти названия статусов на те, которые реально прописаны у тебя в Booking.BookStatus
        try:
            context['upcoming_bookings'] = bookings.filter(
                status__in=[Booking.BookStatus.PENDING, Booking.BookStatus.ACTIVE]
            )
            context['completed_bookings'] = bookings.filter(
                status=Booking.BookStatus.COMPLETED
            )
            context['cancelled_bookings'] = bookings.filter(
                status__in=[Booking.BookStatus.CANCELLED, Booking.BookStatus.MISSED]
            )
        except AttributeError:
            # Если у тебя статусы хранятся строками (как я писал изначально), 
            # удали блок try-except и оставь вариант со строками.
            context['upcoming_bookings'] = bookings.filter(status__in=['pending', 'active'])
            context['completed_bookings'] = bookings.filter(status='completed')
            context['cancelled_bookings'] = bookings.filter(status__in=['cancelled', 'missed'])
        
        return context
    
class Profile(DetailView):
    model = Client
    context_object_name = 'client'
    template_name = 'UserActivity/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        client_data = self.request.user
        context['client_data'] = client_data
        
        return context
    

    
class ClientAbandonBookingsView(DeleteView):
    model = Booking
    template_name = 'UserActivity/client_bookings.html'
    success_url = reverse_lazy('my_bookings')
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.can_edit_or_delete():
            messages.error(request, "Запись , осталось менее 12 часов до начала.")
            return redirect('my_bookings')
            
        return super().dispatch(request, *args, **kwargs)
    
    
    
class EditBookingView(UpdateView):
    model = Booking
    form_class = EditBookingForm
    template_name = 'UserActivity/edit_booking.html'
    success_url = reverse_lazy('my_bookings')
    
    def get_queryset(self):
        return Booking.objects.filter(user_id=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.can_edit_or_delete():
            messages.error(request, "Запись нельзя изменить, осталось менее 12 часов до начала.")
            return redirect('my_bookings')
            
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Запись успешно обновлена!")
        return super().form_valid(form)
    
class CarServiceHistory(ListView):
    model = Booking
    template_name = 'UserActivity/car_history.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        self.car = get_object_or_404(UserCar, vin=self.kwargs['vin'], user_id=self.request.user)
        books = Booking.objects.filter(
            user_car=self.car)
        # Достаем только завершенные записи для найденной машины
        return Booking.objects.filter(
            user_car=self.car,
            status='completed'
        ).select_related(
            'service_id'
        ).prefetch_related(
            'equipment',
            'bookingdetail_set',
            'bookingdetail_set__bookingsparepart_set__part'
        ).order_by('-date', '-start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = self.car
        return context
    
    
@login_required
def start_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user_id=request.user.id)
        
        if booking.status == Booking.BookStatus.ACTIVE:
            return redirect('my_bookings')
            
        try:
            # Вся магия происходит здесь
            booking.start_session()
            messages.success(request, 'Обслуживание успешно начато! Время пошло.')
        except ValidationError as e:
            # Если опоздал или пришел слишком рано
            messages.error(request, e.message)
            
    return redirect('my_bookings')
    
@login_required
def complete_booking_and_pay(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user_id=request.user.id)
    
    if request.method == 'POST':
        # 1. Фиксируем завершение в базе
        booking.complete_session()
        
        # 2. Создаем платеж в ЮKassa
        # Сумма берется из поля total_price (которое должно быть рассчитано при создании или здесь)
        idempotence_key = str(uuid.uuid4())
        
        # URL, куда ЮKassa вернет клиента после оплаты (твоя страница успеха)
        return_url = request.build_absolute_uri(reverse('my_bookings')) 

        try:
            payment = Payment.create({
                "amount": {
                    "value": str(booking.total_price),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url
                },
                "capture": True,
                "description": f"Оплата бокса №{booking.box.name}. Бронь №{booking.id}"
            }, idempotence_key)

            # Сохраняем ID платежа, чтобы потом проверить статус
            booking.payment_id = payment.id
            booking.save()

            # Редирект на «окно оплаты»
            return redirect(payment.confirmation.confirmation_url)

        except Exception as e:
            messages.error(request, 'Ошибка платежной системы. Обратитесь к администратору.')
            return redirect('my_bookings')
            
    return redirect('my_bookings')

