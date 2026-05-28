from django import forms
from .models import Product,Boarding


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'barcode', 'purchase_price', 'sale_price', 'quantity', 'expiry_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: شامبو قطط'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'باركود اختياري'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        

class BoardingForm(forms.ModelForm):
    class Meta:
        model = Boarding
        fields = [
            'owner_name',
            'phone',
            'pet_name',
            'pet_type',
            'treatment_type',
            'daily_price',
            'treatment_price',
            'notes',
        ]

        widgets = {
            'owner_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: أحمد محمد'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 0790000000'}),
            'pet_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: لولو'}),
            'pet_type': forms.Select(attrs={'class': 'form-select'}),
            'treatment_type': forms.Select(attrs={'class': 'form-select'}),
            'daily_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 5.00', 'step': '0.01'}),
            'treatment_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 10.00', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'ملاحظات عن الحيوان أو العلاج'}),
        }
