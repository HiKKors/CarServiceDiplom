from django.shortcuts import redirect, render, get_object_or_404

from django.forms import modelformset_factory
from django.contrib import messages
from django.http import HttpResponse

from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView

from openpyxl import Workbook

from autoService.models import Box, Equipment, AutoService, Booking, Staff
from UserActivity.models import Review
from .forms import AddAutoServiceDataForm, EquipmentFormSet, BoxForm, EquipmentForm, AddStaffForm

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

            
            box_count = box_form.cleaned_data['box_count']
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
        
        context['equipments'] = equipment_list
        context['reviews'] = review_list
        
        bookings = Booking.objects.filter(service_id = self.object.id).order_by('date')
        for book in bookings:
            print(f'{book.date}, {book.start_time} - {book.end_time}')
        
        return context
    
def get_service_mounth_report_view(request, service_id):
    print('REPORT')
    print(service_id)
    response = HttpResponse(content_type='application/ms-excel; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
    
    wb = Workbook()
    ws = wb.active
    ws.title = 'AutoService'
    
    headers = ['Name', 'count']
    ws.append(headers)
    
    service = AutoService.objects.get(id=service_id)
    bookings = Booking.objects.filter(service_id = service_id)
    
    ws.append([service.name, len(bookings)])
    
    wb.save(response)
    return response

class EditAutoServiceView(TemplateView):
    template_name = 'admin_templates/edit_autoservice.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auto_service = get_object_or_404(AutoService, id=self.kwargs['pk'])  # Получаем объект автосервиса

        start_working_time, end_working_time = auto_service.workingHours.split('-')
        
        equipment = Equipment.objects.filter(service_id = auto_service.id)
        boxes = Box.objects.filter(service_id = auto_service.id)
        
        context['auto_service_form'] = AddAutoServiceDataForm(
            instance=auto_service,
            initial={
                'name': auto_service.name,
                'description': auto_service.description,
                'address': auto_service.address,
                'start_working_time': start_working_time,
                'end_working_time': end_working_time,
            }
        )  
        
        EquipmentFormSet = modelformset_factory(Equipment, form=EquipmentForm, extra=0)
        context['equipment_formset'] = EquipmentFormSet(queryset=equipment)

        # Передаем количество боксов
        context['box_form'] = BoxForm(initial={'box_count': boxes.count()})
        
        context['service_id'] = auto_service.id
        
        return context
    
    def post(self, request, *args, **kwargs):
        service_id = self.kwargs['pk']
        
        auto_service = get_object_or_404(AutoService, id=service_id)
        auto_service_form = AddAutoServiceDataForm(instance=auto_service, data=request.POST)
        
        
        equipment = Equipment.objects.filter(service_id = service_id)
        equipment_form = EquipmentForm(data=request.POST)
        
        boxes = Box.objects.filter(service_id = service_id)
        box_form = BoxForm(data=request.POST)
        
        if 'save_autoservice' in request.POST:
            if auto_service_form.is_bound and auto_service_form.is_valid():
                print(auto_service_form)
                service_name = request.POST.get('name')
                service_desc = request.POST.get('description')
                service_address = request.POST.get('address')
                
                start_day = request.POST.get('start_working_time')
                end_day = request.POST.get('end_working_time')
                
                service_working_hours = start_day + '-' + end_day
                
                auto_service.name = service_name
                auto_service.description = service_desc
                auto_service.address = service_address
                auto_service.workingHours = service_working_hours
                
                auto_service.save()
                logger.info(f'успешное обновление данных автосервиса {auto_service.name}')
            else:
                logger.warning(f'ошибка при обновлении данных автосервиса {auto_service.name}')   
                
        elif 'save_equipment' in request.POST:
            if equipment_form.is_bound and equipment_form.is_valid():
                equipment_form.save()
                logger.info(f'успешное обновление данных оборудования автосервиса {auto_service.name}')
            else:
                logger.warning(f'ошибка обновления данных оборудования автосервиса {auto_service.name}')      
        elif 'save_box' in request.POST:
            if box_form.is_bound and box_form.is_valid():
                box_count = box_form.cleaned_data['box_count']      
                print(box_count, 'box_count')
                if boxes.count() < box_count:
                    for i in range(box_count - boxes.count()):
                        Box.objects.create(service_id=AutoService.objects.get(id=service_id), name=i)
                elif boxes.count() > box_count:
                    for i in range(boxes.count() - box_count):
                        Box.objects.filter(service_id=service_id).last().delete()
                logger.info(f'успешное обновление данных боксов автосервиса {auto_service.name}')
            else:
                logger.warning(f'ошибка обновления данных боксов автосервиса {auto_service.name}')
        
        return redirect('my_services')
    
    
class AllBookingsView(ListView):
    queryset = Booking.objects.all()
    template_name = 'admin_templates/all_bookings.html'
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        admin_services = AutoService.objects.filter(admin = self.request.user)
        services_id = [i.id for i in admin_services]
        bookings = Booking.objects.filter(service_id__in=services_id)
        
        return bookings
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['all_bookings'] = self.get_queryset()
        
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