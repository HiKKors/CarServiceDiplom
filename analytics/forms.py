from django import forms
from .models import Expenses

class AddExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['category', 'amount', 'date', 'description']
        
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }