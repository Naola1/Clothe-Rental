from django import forms
from .models import Rental

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['duration', 'rental_date', 'return_date', 'notes']
        widgets = {
            'rental_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'duration': 'Rental Duration',
            'rental_date': 'Rental Date',
            'notes': 'Additional Notes (Optional)',
        }
