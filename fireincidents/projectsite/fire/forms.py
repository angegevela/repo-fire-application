from django import forms
from .models import FireTruck, Incident, Locations, FireStation, Firefighters, WeatherConditions


class LocationsForm(forms.ModelForm):
    class Meta:
        model = Locations
        fields = ['name', 'latitude', 'longitude', 'address', 'city', 'country']

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['location', 'date_time', 'severity_level', 'description']

class FireStationForm(forms.ModelForm):
    class Meta:
        model = FireStation
        fields = ['name', 'latitude', 'longitude', 'address','city','country']

class FireFightersForm(forms.ModelForm):
    class Meta:
        model = Firefighters
        fields = ['name', 'station', 'experience_level', 'rank']

class FireTruckForm(forms.ModelForm):
    class Meta:
        model = FireTruck
        fields = ['truck_number', 'model', 'capacity', 'station']

class WheatherConditionsForm(forms.ModelForm):
    class Meta:
        model = WeatherConditions
        fields = ['incident', 'temperature', 'humidity', 'wind_speed', 'weather_description']