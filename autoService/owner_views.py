from django.shortcuts import redirect, render, get_object_or_404

from django.forms import modelformset_factory
from django.contrib import messages

from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
# from django.views.generic.edit import DeleteView
from django.utils.timezone import now
from django.db.models import Avg

from autoService.models import Box, Equipment, AutoService, Booking, Staff
from UserActivity.models import Review
from .forms import AddAutoServiceDataForm, EquipmentFormSet, BoxForm, EquipmentForm, AddStaffForm

from .filters import AllBookingsFilterForm

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

def add_auto_service(request):
    user = request.user
    if request.method == 'POST':
        auto_service = AutoService()
        box_form = BoxForm(request.POST)
        
        equipment_names = request.POST.getlist('equipment_name')
        equipment_prices = request.POST.getlist('equipment_price')
        
        print(equipment_names, equipment_prices)
        
        if box_form.is_valid():
            # указываем админа
            auto_service.owner = user
            
            # получаем данные
            service_name = request.POST.get('name')
            service_desc = request.POST.get('description')
            service_address = request.POST.get('address')
            
            # формируем рабочие часы
            start_day = request.POST.get('start_working_time')
            end_day = request.POST.get('end_working_time')
            
            service_working_hours = start_day + '-' + end_day
            
            # сохраняем в модель
            auto_service.name = service_name
            auto_service.description = service_desc
            auto_service.address = service_address
            auto_service.workingHours = service_working_hours
            
            # сохраняем в бд
            auto_service.save()
            
            for name, price in zip(equipment_names, equipment_prices):
                Equipment.objects.create(name = name, price = price, service_id = auto_service)

            
            box_count = box_form.cleaned_data['count'] 

    
            for i in range(1, box_count + 1):
                Box.objects.create(name=str(i), service_id=auto_service)
            for i in range(1, box_count + 1):
                Box.objects.create(name=i, service_id=auto_service)
            return redirect('my_services')
        elif not user.is_admin:
            messages.error(request=request, message='Клиент не может создавать автосервис')
        else:
            messages.success(request=request, message='Ошибка добавления')
    else: 
        service_form = AddAutoServiceDataForm()
        equipment_formset = EquipmentFormSet(instance=None)
        box_form = BoxForm()
        
    return render(request, 'admin_templates/add_service.html', {
        'service_form': service_form,
        'equipment_formset': equipment_formset,
        'box_form': box_form,
    })
    
    
class MyServicesView(ListView):
    queryset = AutoService.objects.all()
    template_name = 'admin_templates/my_services.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        admin_services = AutoService.objects.filter(owner=self.request.user.id)
        
        context['admin_services'] = admin_services
        
        return context
    
class MyServiceManagmentView(DetailView):
    model = AutoService
    context_object_name = 'my_service'
    template_name = 'admin_templates/my_service_managment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_id = self.object.id
        
        equipment_list = Equipment.objects.filter(service_id = service_id)
        review_list = Review.objects.filter(service_id = service_id)
        boxes = Box.objects.filter(service_id = service_id)
        active_sessions_count = Booking.objects.filter(service_id = service_id).filter(status = 'active').count()
        
        today_date = now().date()
        today_bookings_count = Booking.objects.filter(service_id = service_id).filter(date = today_date).count()
        
        rating = review_list.aggregate(rating=Avg('mark'))
        
        context['equipments'] = equipment_list
        context['reviews'] = review_list
        context['boxes'] = boxes
        context['active_sessions_count'] = active_sessions_count
        context['today_bookings_count'] = today_bookings_count
        context['rating'] = round(rating['rating'], 1) if rating['rating'] else 0
        
        bookings = Booking.objects.filter(service_id = self.object.id).order_by('date')
        for book in bookings:
            print(f'{book.date}, {book.start_time} - {book.end_time}')
        
        return context


class EditAutoServiceView(TemplateView):
    template_name = 'admin_templates/edit_autoservice.html'

    def get_auto_service(self):
        return get_object_or_404(AutoService, id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auto_service = self.get_auto_service()

        # Разбираем часы работы для формы
        try:
            start_working_time, end_working_time = auto_service.workingHours.split('-')
        except (ValueError, AttributeError):
            start_working_time, end_working_time = "09:00", "21:00"

        # Основная форма
        context['auto_service_form'] = AddAutoServiceDataForm(
            instance=auto_service,
            initial={
                'start_working_time': start_working_time,
                'end_working_time': end_working_time,
            }
        )

        # Оборудование (FormSet)
        EquipmentFormSet = modelformset_factory(Equipment, form=EquipmentForm, extra=0, can_delete=True)
        context['equipment_formset'] = EquipmentFormSet(
            queryset=Equipment.objects.filter(service_id=auto_service)
        )

        # Боксы (используем поле 'count' из нашей обновленной формы)
        context['box_form'] = BoxForm(initial={'count': auto_service.box_set.count()})
        context['service_id'] = auto_service.id
        context['my_service'] = auto_service # Для заголовков в шаблоне
        
        return context

    def post(self, request, *args, **kwargs):
        auto_service = self.get_auto_service()
        
        # 1. СОХРАНЕНИЕ ОСНОВНЫХ ДАННЫХ
        if 'save_autoservice' in request.POST:
            form = AddAutoServiceDataForm(request.POST, instance=auto_service)
            if form.is_valid():
                # Автоматически собираем workingHours перед сохранением
                start = form.cleaned_data.get('start_working_time')
                end = form.cleaned_data.get('end_working_time')
                auto_service.workingHours = f"{start}-{end}"
                form.save()
                messages.success(request, f'Данные сервиса "{auto_service.name}" обновлены.')
            else:
                messages.error(request, 'Ошибка в данных автосервиса.')

        # 2. СОХРАНЕНИЕ ОБОРУДОВАНИЯ (Вот тут была главная ошибка)
        elif 'save_equipment' in request.POST:
            EquipmentFormSet = modelformset_factory(Equipment, form=EquipmentForm, extra=0, can_delete=True)
            formset = EquipmentFormSet(request.POST, queryset=Equipment.objects.filter(service_id=auto_service))
            
            if formset.is_valid():
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.service_id = auto_service # Привязываем к сервису
                    instance.save()
                
                # Обработка удаления (тех, где поставили галочку DELETE)
                for obj in formset.deleted_objects:
                    obj.delete()
                    
                messages.success(request, 'Список оборудования обновлен.')
            else:
                messages.error(request, 'Ошибка при сохранении оборудования.')

        # 3. СОХРАНЕНИЕ БОКСОВ
        elif 'save_box' in request.POST:
            form = BoxForm(request.POST)
            if form.is_valid():
                new_count = form.cleaned_data['count'] # Используем 'count'
                current_boxes = auto_service.box_set.all().order_by('id')
                current_count = current_boxes.count()

                if new_count > current_count:
                    # Создаем новые боксы с красивыми именами (1, 2, 3...)
                    for i in range(current_count + 1, new_count + 1):
                        Box.objects.create(service_id=auto_service, name=str(i))
                elif new_count < current_count:
                    # Удаляем лишние с конца
                    to_delete = current_boxes[new_count:]
                    for box in to_delete:
                        # Логика на 2 шага вперед: проверка на бронирования
                        if box.booking_set.filter(status__in=['pending', 'active']).exists():
                            messages.error(request, f'Нельзя удалить бокс {box.name}, в нем есть активные записи!')
                            return redirect('edit_autoservice', pk=auto_service.id)
                        box.delete()
                
                messages.success(request, 'Количество боксов успешно изменено.')

        return redirect('my_service_managment', auto_service.id)
    
    
class AllBookingsView(ListView):
    model = Booking
    template_name = 'admin_templates/all_bookings.html'
    context_object_name = 'all_bookings'
    
    def get_queryset(self):
        qs = Booking.objects.filter(service_id__owner=self.request.user)
        
        self.filterset = AllBookingsFilterForm(self.request.GET, queryset=qs)
        
        box_id = self.request.GET.get('box')
        if box_id:
            qs = qs.filter(box_id=box_id)
            
        if self.filterset.is_valid():
            filtered_qs = self.filterset.qs
        else:
            filtered_qs = self.queryset
        
        logger.info(f'Фильтр {self.request.GET}, найдено: {filtered_qs.count()} совпадений')
        
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        context['form'] = self.filterset.form
        
        return context
    
class MyServicesForStaffView(ListView):
    model = AutoService
    template_name = 'admin_templates/my_services_staff.html'
    context_object_name = 'services'

    def get_queryset(self):
        return AutoService.objects.filter(owner=self.request.user)
    
class MyStaffView(ListView):
    queryset = Staff.objects.all()
    template_name = 'admin_templates/service_staff.html'
    context_object_name = 'staff_list'
    
    def get_queryset(self):
        service_id = self.kwargs['service_id']
        return Staff.objects.filter(service_id=service_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = AutoService.objects.get(id=self.kwargs['service_id'])
        print(context['staff_list'])
        return context
    
def add_staff_view(request, service):
    if request.method == 'POST':
        form = AddStaffForm(request.POST)
        if form.is_valid():
            service_id = get_object_or_404(AutoService, id=service).id
            # print('SERVICE', service_id.id)
            staff = form.save(commit=False)
            staff.service = AutoService.objects.get(id=service_id)
            
            staff.name = form.cleaned_data['name']
            staff.surname = form.cleaned_data['surname']
            staff.salary = form.cleaned_data['salary']
            
            staff.save()
            
            return redirect('my_staff', service_id=service_id)
            
    else:
        form = AddStaffForm()
        
        return render(request, 'admin_templates/add_staff.html', {'form': form, 'service_id': service})
    
@login_required
@require_POST
def toggle_box_status(request, box_id):
    """Смена статуса открыт/закрыт для конкретного бокса"""
    box = get_object_or_404(Box, id=box_id)
    
    # Проверка прав доступа (только владелец сервиса)
    if box.service_id.owner != request.user:
        messages.error(request, "Доступ запрещен.")
        return redirect('my_service', service_id=box.service_id.id)
    
    # Логика переключения
    box.is_opened = not box.is_opened
    box.save()
    
    status_msg = "открыт для бронирования" if box.is_opened else "закрыт на техническое обслуживание"
    messages.success(request, f"Бокс №{box.name} успешно {status_msg}.")
    
    return redirect('my_service_managment', pk=box.service_id.id)

@login_required
@require_POST
def toggle_equipment_status(request, equipment_id):
    """Смена статуса доступности оборудования"""
    equipment = get_object_or_404(Equipment, id=equipment_id)
    
    # Защита доступа
    if equipment.service_id.owner != request.user:
        messages.error(request, "Доступ запрещен.")
        return redirect('my_services')
    
    # Инвертируем статус
    equipment.is_available = not equipment.is_available
    equipment.save()
    
    status_msg = "теперь доступно" if equipment.is_available else "временно недоступно"
    messages.success(request, f"Оборудование '{equipment.name}' {status_msg}.")
    
    return redirect('my_service_managment', pk=equipment.service_id.id)