from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['subject', 'description', 'price']
        
        widgets = {
            'subject': forms.Select(attrs={
                'style': 'background: #1a1a1a !important; color: white !important; border: 1px solid #333 !important; border-radius: 12px !important; padding: 12px !important; margin-bottom: 15px; width: 100%; display: block;'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Что нужно сделать?',
                'style': 'background: #1a1a1a !important; color: white !important; border: 1px solid #333 !important; border-radius: 12px !important; padding: 12px !important; margin-bottom: 15px; width: 100%; display: block;'
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': 'Бюджет в тенге',
                'style': 'background: #1a1a1a !important; color: white !important; border: 1px solid #333 !important; border-radius: 12px !important; padding: 12px !important; margin-bottom: 15px; width: 100%; display: block;'
            }),
        }