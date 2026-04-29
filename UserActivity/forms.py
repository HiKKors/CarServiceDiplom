from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import inlineformset_factory

from .models import UserCar
from autoService.models import AutoService, Equipment, Box, Booking


from django import forms
from .models import UserCar 

class UserCarForm(forms.ModelForm):
    class Meta:
        model = UserCar
        # Добавили generation, engine_capacity, power
        fields = ['vin', 'make', 'model', 'generation', 'year', 'engine_capacity', 'power', 'current_mileage'] 
        widgets = {
            'vin': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Например: XTA21000000000000'
            }),
            'make': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Например: Toyota'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Например: Camry'
            }),
            'generation': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Например: XV70'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Например: 2020'
            }),
            'engine_capacity': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Например: 2.5',
                'step': '0.1' # Позволяет вводить дробные числа
            }),
            'power': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Например: 181'
            }),
            'current_mileage': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'vin': 'VIN-номер',
            'make': 'Марка',
            'model': 'Модель',
            'generation': 'Поколение',
            'year': 'Год выпуска',
            'engine_capacity': 'Объем двигателя (л)',
            'power': 'Мощность (л.с.)',
            'current_mileage': 'Пробег (км)',
        }
        
class EditBookingForm(forms.ModelForm):
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
    box = forms.ModelChoiceField(queryset=Box.objects.all(), widget=forms.Select(attrs={
        'class': 'booking-box-select',
        'name': 'booking-box'
    }))
    equipment = forms.ModelMultipleChoiceField(queryset=Equipment.objects.all(), widget=forms.CheckboxSelectMultiple(attrs={
        'class': 'booking-equipment-select',
        'name': 'booking-equipment'
    }))
    comment = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'booking-comment-input',
        'name': 'booking-comment',
        'placeholder': 'Введите предполагаемые работы'
    }))
    
    class Meta:
        model = Booking
        fields = ('date', 'start_time', 'end_time', 'box', 'equipment', 'comment')
        
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        box = cleaned_data.get('box')

        if date and start_time and end_time and box:
            # 1. Защита от дурака: конец раньше начала
            if start_time >= end_time:
                raise forms.ValidationError("Время окончания должно быть позже времени начала.")

            # 2. Проверка пересечений в выбранном боксе
            conflicts = Booking.objects.filter(
                box=box,
                date=date,
                status__in=['pending', 'active']
            ).exclude(pk=self.instance.pk)

            for conflict in conflicts:
                if start_time < conflict.end_time and end_time > conflict.start_time:
                    raise forms.ValidationError("Выбранный бокс на это время уже занят. Измените время или выберите другой бокс.")
                    
        return cleaned_data



# BoxFormSet = inlineformset_factory(
#     AutoService,
#     Box,
#     form=BoxForm,
#     extra=1,
#     can_delete=True
# )