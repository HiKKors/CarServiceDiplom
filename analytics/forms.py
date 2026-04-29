from django import forms
from .models import Expenses

class AddExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['title', 'amount', 'date', 'category', 'description']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Покупка оборудования'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            # Используем type="date", чтобы браузер сам нарисовал удобный календарик
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Необязательный комментарий...'}),
        }