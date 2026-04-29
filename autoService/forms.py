from django import forms

from django.forms import inlineformset_factory, modelformset_factory

from .models import Booking, Box, Equipment, AutoService, BookingSparePart, BookingDetail, SparePart, Staff
from UserActivity.models import Review, UserCar
# from user.models import UserCar
from django_select2.forms import ModelSelect2Widget, ModelSelect2TagWidget

class AddAutoServiceDataForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'service-name-input',
        'placeholder': 'Введите название автосервиса',
        'name': 'service-name',
        'label': 'Название'
    }))
    description = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'service-description-input',
        'placeholder': 'Введите описание',
        'name': 'service-description'
    }))
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'service-address-input',
        'placeholder': 'Введите адрес автосервиса',
        'name': 'service-address'
    }))
    start_working_time = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'service-start-working-time-input',
        'name': 'service-start-working-time'
    }))
    end_working_time = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'service-end-working-time-input',
        'name': 'service-end-working-time'
    }))
    
    class Meta:
        model = AutoService
        fields = ('name', 'description', 'address', 'start_working_time', 'end_working_time')
    
class EquipmentForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'service-equipment-name-input',
        'name': 'service-equipment-name'
    }))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'service-equipment-price-input',
        'name': 'service-equipment-price'
    }))
    
    class Meta:
        model = Equipment
        fields = ('name', 'price')

class BoxForm(forms.Form):
    # Изменяем на 'count', чтобы совпадало с твоим шаблоном
    count = forms.IntegerField(
        label="Количество боксов",
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'min': 1
        })
    )

class SparePartWidget(ModelSelect2Widget):
    model = SparePart
    search_fields = ['name__icontains', 'article__icontains']
    attrs = {
        'data-tags': 'true',
        'data-placeholder': 'Введите название или выберите запчасть',
    }

class BookingForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'booking-date-input',
        'name': 'booking-date'
    }))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={
        'type': 'time',
        'class': 'booking-start-input',
        'name': 'booking-start'
    }))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={
        'type': 'time',
        'class': 'booking-end-input',
        'name': 'booking-end'
    }))
    # отфильтровать машины по id пользователя
    user_car_id = forms.ModelChoiceField(queryset=UserCar.objects.all(), widget=forms.Select(attrs={
        'class': 'booking-user-car-select',
        'name': 'booking-user-car'
    }))
    box = forms.ModelChoiceField(queryset=Box.objects.all(), widget=forms.Select(attrs={
        'class': 'booking-box-select',
        'name': 'booking-box'
    }))
    equipment = forms.ModelMultipleChoiceField(queryset=Equipment.objects.all(), widget=forms.CheckboxSelectMultiple(attrs={
        'class': 'booking-equipment-select',
        'name': 'booking-equipment'
    }))

    
    class Meta:
        model = Booking
        fields = ('date', 'start_time', 'end_time', 'box', 'equipment')
        
class BookingMainDetailForm(forms.ModelForm):
    planned_works = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'booking-comment-input',
        'placeholder': 'Введите предполагаемые работы',
    })
    )
    
    mileage = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'booking-mileage-input',
        'placeholder': 'Введите пробег на данный момент',
    })
    )
    
    class Meta:
        model = BookingDetail
        fields = ('planned_works', 'mileage',)
        
class BookingSparePartForm(forms.ModelForm):
        model = BookingSparePart
        fields = ('part', 'quantity',)
        widgets = {
            'part': ModelSelect2TagWidget(
                model=SparePart,
                search_fields=['name__icontains'],
            )
        }
        
        
        def clean_part(self):
            part = self.cleaned_data['part']
            if isinstance(part, str):
                # Пользователь ввел новое значение (еще не объект SparePart)
                new_part = SparePart.objects.create(name=part, article="")
                return new_part
            return part         
    
class AddStaffForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'name': 'staff-name-input',
        'class': 'staff-input',
    }))
    surname = forms.CharField(widget=forms.TextInput(attrs={
        'name': 'staff-surname-input',
        'class': 'staff-input',
    }))
    salary = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'staff-input',
        'name': 'staff-salary',
        'type': 'number',
        'min': 0,
    }))
    
    class Meta:
        model = Staff
        fields = ('name', 'surname', 'salary')
        
    
class ReviewForm(forms.ModelForm):
    mark = forms.IntegerField(widget=forms.HiddenInput()) # Скрытое поле, значение в которое запишет JS
    comment = forms.CharField(
        label="Ваш отзыв",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Расскажите, как все прошло...',
            'rows': 4
        })
    )
    
    class Meta:
        model = Review
        fields = ('mark', 'comment')
    
        
        
BookingSparePartFormSet = modelformset_factory(
    BookingSparePart, 
    form=BookingSparePartForm, 
    fields=('part', 'quantity'),
    extra=1,
    can_delete=True
)

# соединияем формы в одну

# к форме AddAutoServiceDataForm добавляем форму EquipmentForm
EquipmentFormSet = inlineformset_factory(
    AutoService,
    Equipment,
    form=EquipmentForm,
    extra=0, # Ставим 0, чтобы пустые строки добавлялись только по кнопке
    can_delete=True,
)