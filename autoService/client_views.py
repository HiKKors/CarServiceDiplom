from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View

from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required

from .models import AutoService, Equipment, Box, BookingEquipment, BookingDetail, SparePart, Booking, BookingSparePart
from UserActivity.models import Review, UserCar
from .forms import BookingForm, BookingMainDetailForm, BookingSparePartForm, BookingSparePartFormSet
from .filters import ServiceFilterForm

from django.forms import modelformset_factory
from django.core.exceptions import ValidationError

import datetime

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

class AllServicesList(ListView):
    queryset = AutoService.objects.all()
    context_object_name = 'services'
    template_name = 'autoService/all_services.html'
    
    
    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ServiceFilterForm(self.request.GET, queryset=queryset)
        if self.filterset.is_valid():
            filtered_qs = self.filterset.qs
        else:
            filtered_qs = self.queryset
            
        logger.info(f"Фильтр: {self.request.GET}, Найдено: {filtered_qs.count()} автосервисов")
        return filtered_qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user_data = self.request.user
        
        active_bookings = Booking.objects.filter(user_id = user_data.id).filter(status='pending')
        print(active_bookings)
        context['user'] = user_data
        context['services'] = self.get_queryset()
        context['cities'] = self.filterset.cities
        context['active_bookings'] = active_bookings
        context['form'] = self.filterset.form
        
        return context
    
    
class ServiceDetail(DetailView):
    model = AutoService
    context_object_name = 'service'
    template_name = 'autoService/service_detail.html' 
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_id = self.object.id
        
        service_data = AutoService.objects.get(id=service_id)
        print(service_data.workingHours)
        current_hour = datetime.datetime.now().time().hour
        service_work_hours = service_data.workingHours
        start_work, end_work = service_work_hours.split('-')
        
        if int(start_work) <= current_hour <= int(end_work):
            context['is_open'] = True
            context['will_close_in'] = int(end_work) - int(current_hour)
        else:
            context['is_open'] = False
            
        equipment_list = Equipment.objects.filter(service_id=service_id)
        # reviews = Review.objects.filter(service_id = service_id)
        
        context['equipment_list'] = equipment_list
        # context['reviews'] = reviews
        return context
    
def create_booking(request, service_id):
    service = get_object_or_404(AutoService, id=service_id)

    if request.method == 'POST':
        print('POST')
        booking_form = BookingForm(request.POST)
        booking_equipment = BookingEquipment()

        equipments = request.POST.getlist('equipment')  
        booking_form.fields['equipment'].queryset = Equipment.objects.filter(service_id=service_id)
        
        box_id = request.POST.get('box')
        box = Box.objects.get(id=box_id)
        
        if booking_form.is_valid():
            
            booking = booking_form.save(commit=False)
            
            booking.user_id = request.user
            booking.service_id = AutoService.objects.get(id=service_id)
            booking.box = box
            if Booking.objects.filter(date = booking.date, start_time = booking.start_time, end_time = booking.end_time, box = booking.box):
                print('Ошибка: бокс и время уже занято')
            
            booking.save()
            
            if len(equipments) > 1:
                print(True)
                for equipment in equipments:
                    print(equipment)
                    BookingEquipment.objects.create(booking_id = booking, equipment_id = Equipment.objects.get(id = equipment))
            elif len(equipments) == 1:
                print('1')
                booking_equipment.equipment_id = Equipment.objects.get(id=equipments[0])
                booking_equipment.booking_id = booking
                booking_equipment.save()

            # return redirect('/%2Fadd_booking_detail', booking_id = booking.id)
            return redirect(f'/create-booking/{service_id}/add_booking_detail/{booking.id}')
    else:
        booking_form = BookingForm()
        
        # booking_form.fields['user_car_id'].queryset = UserCar.objects.filter(user = request.user)
        booking_form.fields['box'].queryset = Box.objects.filter(service_id = service_id)
        # booking_form.fields['box'].name = 'box'
        
        booking_form.fields['equipment'].queryset = Equipment.objects.filter(service_id = service_id)
        # задаем имя оборудования для шаблона
        # booking_form.fields['equipment'].name = 'equipment'
        
        availability_data = None
        selected_date = request.GET.get('date')
        
        if selected_date:
            try:
                target_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
                availability_data = service.get_availability_for_date(target_date)
            except ValueError:
                pass
        
        # print(booking_form.equipment)
        
    
    return render(request, 'autoService/create-booking.html', {
        'form': booking_form, 
        'service_id': service_id,
        'availability_data': availability_data,
        'selected_date': selected_date or timezone.now().date().isoformat()
        
    })

def add_booking_detail(request, service_id, booking_id):
    booking = Booking.objects.get(id = booking_id)
    
    if request.method == 'POST':
        print('МЕТОД POST ДЕТАЛИ БРОНИ')
        detail_form = BookingMainDetailForm(request.POST)
        formset = BookingSparePartFormSet(request.POST, queryset=BookingSparePart.objects.none())
        
        print(formset.errors)
        if detail_form.is_valid() and formset.is_valid():
            print('ФОРМА ОСНОВНЫХ ДЕТАЛЕЙ БРОНИ ВАЛИДНА')
            booking_detail = detail_form.save(commit=False)
            booking_detail.booking = booking
            booking_detail.save()
            
            print('ВАЛИДНОСТЬ ФОРМСЕТА', formset.is_valid())
            print(formset.errors)
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    print('СОХРАНЕНИЕ ЗАПЧАСТЕЙ')
                    part = form.cleaned_data['part']
                    quantity = form.cleaned_data['quantity']
                    
                    print(part)
                    print(quantity)
                    
                    BookingSparePart.objects.create(
                        booking_detail=booking_detail,
                        part=part,
                        quantity=quantity
                    )
                    
            return redirect(f'/%2Fservice-info/{service_id}')
    
    else:
        detail_form = BookingMainDetailForm()
        formset = BookingSparePartFormSet(queryset=BookingSparePart.objects.none())
        
    return render(
        request, 'autoService/add_booking_details.html', {
            'form': detail_form,
            'formset': formset,
            'booking': booking,
            'service_id': service_id,
            'booking_id': booking_id
        }
    )

class BookingManagment(DetailView):
    model = Booking
    context_object_name = 'booking_managment'
    template_name = 'autoService/booking_managment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.object.id
        
        booking_data = get_object_or_404(Booking, id=booking_id)
        print(booking_data.status)
        service_data = booking_data.service_id
        # car_data = get_object_or_404(UserCar, id=booking_data.user_car_id)
        
        context['booking_data'] = booking_data
        context['service_data'] = service_data
        
        return context
    
class PendingBookings(ListView):

    context_object_name = 'pending_bookings'
    template_name = 'autoService/pending_bookings.html'
    
    def get_queryset(self):
        user = self.request.user
        queryset = Booking.objects.filter(user_id = user.id).filter(status='pending')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        pending_bookings = Booking.objects.filter(user_id = user.id).filter(status='pending')
        
        context['pending_bookings'] = pending_bookings
        
        return context
        
        
# @login_required
def mark_arrived(request, booking_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST запросы разрешены'}, status=405)
    
    booking = get_object_or_404(Booking, id=booking_id, user_id=request.user.id)
    
    try:
        booking.mark_arrived()
        logger.info(f"Пользователь {request.user.email} отметил прибытие по брони {booking_id}")
        return JsonResponse({'status': 'ok', 'new_status': booking.status})
    except ValidationError as e:
        error_message = e.message if isinstance(e.message, str) else e.message[0]
        logger.warning(f"Ошибка при отметке прибытия: {error_message}")
        return JsonResponse({'error': str(error_message)}, status=400)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return JsonResponse({'error': 'Внутренняя ошибка сервера'}, status=500)

# @login_required
def mark_completed(request, booking_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST запросы разрешены'}, status=405)
    
    booking = get_object_or_404(Booking, id=booking_id, user_id=request.user.id)
    
    try:
        booking.mark_completed()
        logger.info(f"Пользователь {request.user.email} завершил бронь {booking_id}")
        return JsonResponse({'status': 'ok'})
    except ValidationError as e:
        error_message = e.message if isinstance(e.message, str) else e.message[0]
        logger.warning(f"Ошибка при завершении брони: {error_message}")
        return JsonResponse({'error': str(error_message)}, status=400)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return JsonResponse({'error': 'Внутренняя ошибка сервера'}, status=500)
    
    
    
    
    
    
#test
from django.http import JsonResponse
from django.utils import timezone
# from datetime import datetime, timedelta
from .models import Box, Booking

def get_boxes(request):
    print('get_boxes')
    service_id = request.GET.get('service_id')
    if not service_id:
        return JsonResponse({'error': 'service_id required'}, status=400)
    
    boxes = Box.objects.filter(service_id=service_id).values('id', 'name')
    return JsonResponse(list(boxes), safe=False)

def get_available_times(request):
    print('доступное время')
    box_id = request.GET.get('box_id')
    # date_str = request.GET.get('date')  # формат: YYYY-MM-DD
    
    if not box_id:
        return JsonResponse({'error': 'box_id and date required'}, status=400)
    
    # try:
    #     date = datetime.strptime(date_str, '%Y-%m-%d').date()
    #     if date < timezone.now().date():
    #         return JsonResponse({'error': 'Нельзя выбрать прошедшую дату'}, status=400)
    # except ValueError:
    #     return JsonResponse({'error': 'Неверный формат даты'}, status=400)
    
    # Получаем все брони для этого бокса на эту дату
    bookings = Booking.objects.filter(
        box_id=box_id,
        # start_time__date=date
    ).values('start_time', 'end_time')
    
    # Преобразуем в удобный формат
    busy_intervals = []
    for b in bookings:
        busy_intervals.append((b['start_time'], b['end_time']))
    
    # Генерируем слоты (например, с 9:00 до 20:00, по 1 часу)
    slots = []
    work_start = 9
    work_end = 20
    duration = 60  # минут
    
    # current = datetime.combine(date, datetime.min.time()).replace(hour=work_start)
    # end_of_day = datetime.combine(date, datetime.min.time()).replace(hour=work_end)
    
    # while current + timedelta(minutes=duration) <= end_of_day:
    #     slot_start = current
    #     slot_end = current + timedelta(minutes=duration)
        
    #     # Проверяем, пересекается ли слот с занятым временем
    #     is_free = True
    #     for busy_start, busy_end in busy_intervals:
    #         if slot_start < busy_end and slot_end > busy_start:
    #             is_free = False
    #             break
        
    #     if is_free:
    #         slots.append({
    #             'start': slot_start.strftime('%H:%M'),
    #             'end': slot_end.strftime('%H:%M')
    #         })
        
    #     current += timedelta(minutes=30)  # шаг 30 мин (можно менять)
    
    return JsonResponse({'slots': slots})


    


