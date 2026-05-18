import os
import io

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render, redirect, get_list_or_404
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
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
from django.forms.utils import ErrorList

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import logging

from yookassa import Configuration, Payment
import uuid

from autoService.models import Booking, BookingDetail
from accounts.models import Client
from .forms import UserCarForm, EditBookingForm
from .models import UserCar, Review

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
        print(form.instance.vin)
        form.instance.user = self.request.user 
        messages.success(self.request, 'Автомобиль успешно добавлен в гараж!')
        return super().form_valid(form)
    
    # def form_invalid(self, form):
    #     print(form.errors.as_data()['vin'])

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



Configuration.account_id = '1339725'
Configuration.secret_key = 'test_8nSYyHEDiVrX--bzO6Mb_TTGv6pehwAG9XcjenftCxs'
    
@login_required
def complete_booking_and_pay(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user_id=request.user.id)
    
    if request.method == 'POST':
        mileage_str = request.POST.get('mileage')
        
        if mileage_str:
            try:
                new_mileage = int(mileage_str)
                car = booking.user_car
                print('БРОНЬ', booking)
                print(car)
                print(car.current_mileage)
                
                # Проверяем, не скрутили ли пробег (или не опечатались ли)
                if car and car.current_mileage is not None and new_mileage < car.current_mileage:
                    messages.error(
                        request, 
                        f"Ошибка: Введенный пробег ({new_mileage} км) меньше текущего ({car.current_mileage} км)."
                    )
                    # Прерываем функцию и возвращаем обратно на страницу
                    return redirect('my_bookings')
                
                # Если все ок, обновляем пробег машины в базе
                if car:
                    car.current_mileage = new_mileage
                    car.save()
                    
            except ValueError:
                messages.error(request, "Ошибка: Пробег должен быть числом.")
                return redirect('my_bookings')
        
        # --- СЧИТАЕМ ПЕРЕРАСХОД ВРЕМЕНИ (OVERTIME) ---
        now = timezone.now()
        
        # Собираем дату и время окончания из базы с учетом часового пояса
        planned_end_dt = timezone.make_aware(
            datetime.combine(booking.date, booking.end_time)
        )
        
        # Даем 5 минут "бесплатно" на выезд из бокса
        grace_period = timedelta(minutes=5)
        
        if now > (planned_end_dt + grace_period):
            overtime = now - planned_end_dt
            overtime_minutes = int(overtime.total_seconds() / 60)
            
            # Штраф: например, 150 руб за каждые начатые 30 минут просрочки
            overtime_periods = (overtime_minutes // 30) + 1 
            penalty_fee = overtime_periods * 150 
            
            # Плюсуем штраф к итоговой сумме в базе
            booking.total_price += penalty_fee
            
            # Предупреждаем клиента
            messages.warning(request, f"Зафиксирован перерасход времени ({overtime_minutes} мин). К оплате добавлен штраф {penalty_fee} руб.")
        # ----------------------------------------------

        booking.status = 'completed'
        booking.save()
        
        return_url = request.build_absolute_uri(reverse('payment_success', args=[booking.id]))
        
        # 2. Создаем платеж в ЮKassa
        idempotence_key = str(uuid.uuid4())
        try:
            payment = Payment.create({
                "amount": {
                    "value": str(booking.total_price), # Обязательно переводим в строку для ЮKassa
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url
                },
                "capture": True,
                "description": f"Оплата бокса №{booking.box.name}. Запись №{booking.id}"
            }, idempotence_key)

            booking.payment_id = payment.id 
            booking.save()

            return redirect(payment.confirmation.confirmation_url)

        except Exception as e:
            print(f"Ошибка ЮKassa: {e}") 
            messages.error(request, "Ошибка платежного шлюза")
            return redirect('my_bookings')
            
    return redirect('my_bookings')

@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user_id=request.user.id)
    
    # Если у брони есть ID платежа, идем проверять его в ЮKassу
    if booking.payment_id:
        try:
            payment = Payment.find_one(booking.payment_id)
            
            # Если ЮKassa подтверждает, что деньги списаны
            if payment.status == 'succeeded':
                # Убедись, что статус 'completed' или 'paid' существует в твоей модели
                booking.status = 'completed' 
                booking.save()
                messages.success(request, 'Оплата успешно завершена! Чек сформирован.')
            elif payment.status == 'pending':
                messages.warning(request, 'Платёж ещё обрабатывается банком.')
            else:
                messages.error(request, 'Платёж отменён или не прошел.')
                
        except Exception as e:
            print(f"Ошибка проверки платежа: {e}")
            messages.error(request, 'Ошибка при связи с банком.')

    return render(request, 'UserActivity/payment_success.html', {'booking': booking})

@login_required
def generate_receipt_pdf(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # создаем буфер в оперативке
    buffer = io.BytesIO()
    
    # холст
    p = canvas.Canvas(buffer)
    
    font_name = 'ArialRegular.ttf' 
    font_path = os.path.join(settings.BASE_DIR, 'UserActivity', 'fonts', font_name)
    
    try:
        pdfmetrics.registerFont(TTFont('RussianFont', font_path))
        p.setFont('RussianFont', 16)
    except Exception as e:
        print(f"ШРИФТ НЕ НАЙДЕН: {e}. Проверьте путь: {font_path}")
        p.setFont('Helvetica', 16) # Запасной вариант (кириллица сломается)

    # --- Рисуем чек ---
    # Координаты (x, y) идут от левого нижнего угла листа
    p.drawString(100, 800, f"Кассовый чек №{booking.id}")
    
    p.setFont('RussianFont', 12)
    p.drawString(100, 770, f"Организация: {booking.service_id.name}")
    p.drawString(100, 750, f"Адрес: {booking.service_id.address}")
    p.drawString(100, 730, f"Клиент: {request.user.first_name} {request.user.last_name}")
    
    p.drawString(100, 700, "-"*60)
    
    p.drawString(100, 680, f"Услуга: Аренда бокса №{booking.box.name}")
    p.drawString(100, 660, f"Дата: {booking.date}")
    p.drawString(100, 640, f"Время: {booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}")
    
    p.drawString(100, 610, "-"*60)
    
    p.setFont('RussianFont', 14)
    p.drawString(100, 580, f"ИТОГО ОПЛАЧЕНО: {booking.total_price} руб.")
    p.drawString(100, 560, "Статус: ОПЛАЧЕНО (ЮKassa)")

    # Завершаем страницу и сохраняем
    p.showPage()
    p.save()
    
    # Смещаем указатель буфера в начало
    buffer.seek(0)

    # Отправляем файл пользователю
    return FileResponse(buffer, as_attachment=True, filename=f'Receipt_{booking.id}.pdf')