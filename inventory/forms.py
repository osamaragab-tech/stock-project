from django import forms
from .models import StockMovement


class StockMovementForm(forms.ModelForm):
	class Meta:
		model = StockMovement
		fields = ['product', 'movement_type', 'quantity', 'description']
		widgets = {
			'product': forms.Select(attrs={'class': 'form-select'}),
			'movement_type': forms.Select(attrs={'class': 'form-select'}),
			'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
			'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
		}