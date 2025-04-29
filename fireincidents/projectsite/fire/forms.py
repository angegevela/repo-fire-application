from django import forms
from .models import FireTruck

class FireTruckForm(forms.ModelForm):
    class Meta:
        model = FireTruck
        fields = ['truck_number', 'model', 'capacity', 'station']
