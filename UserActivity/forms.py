from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import inlineformset_factory

from .models import UserCar
from autoService.models import AutoService, Equipment, Box, Booking


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
        



# BoxFormSet = inlineformset_factory(
#     AutoService,
#     Box,
#     form=BoxForm,
#     extra=1,
#     can_delete=True
# )