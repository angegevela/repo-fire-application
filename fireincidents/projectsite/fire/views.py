from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Locations, Incident, FireStation


class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"


def map_station(request):
    fireStations = FireStation.objects.values('name', 'latitude', 'longitude')

    fireStations_list = []

    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])  

    context = {
        'fireStations': fireStations_list, 
    }
    return render(request, 'map_station.html', context)