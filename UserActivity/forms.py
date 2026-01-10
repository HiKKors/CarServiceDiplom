from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import inlineformset_factory

from .models import UserCar
from autoService.models import AutoService, Equipment, Box, Booking
   
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
    box_count = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'service-box-number-input',
        'name': 'service-box-number',
        'min': 1
    }))
    
    class Meta:
        model = Box
        fields = ('name',)
        

class UserCarForm(forms.ModelForm):
    vin = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'user-car-vin-input',
        'name': 'user-car-vin'
    }))
    make = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'user-car-make-input',
        'name': 'user-car-make'
    }))
    model = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'user-car-model-input',
        'name': 'user-car-model'
    }))
    generation = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'user-car-generation-input',
        'name': 'user-car-generation'
    }))
    year = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'user-car-model-input',
        'name': 'user-car-model',
        'min': 1900
    }))
    engine_capacity = forms.FloatField(widget=forms.NumberInput(attrs={
        'class': 'user-car-engine-capacity-input',
        'name': 'user-car-engine-capacity',
        'min': 0,
        'step': 0.1
    }))
    power = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'user-car-power-input',
        'name': 'user-car-power',
        'min': 0
    }))
    
    class Meta:
        model = UserCar
        fields = ('vin', 'make', 'model', 'generation', 'year', 'engine_capacity', 'power')
        

# соединияем формы в одну

# к форме AddAutoServiceDataForm добавляем форму EquipmentForm
EquipmentFormSet = inlineformset_factory(
    AutoService,    # родительская модель
    Equipment,  # дочерняя
    form = EquipmentForm,
    extra=1,    # Количество пустых форм, которые отображаются по умолчанию  (хз что это значит)
    can_delete=True,  # При удалении записи, можно удалить все записи в EquipmentFormSet
)

# BoxFormSet = inlineformset_factory(
#     AutoService,
#     Box,
#     form=BoxForm,
#     extra=1,
#     can_delete=True
# )