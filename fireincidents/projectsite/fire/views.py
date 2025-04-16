from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Locations, Incident, FireStation


from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth


from django.db.models import Count
from datetime import datetime


class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    def get_queryset(self, *args, **kwargs):
        pass

def PieCountbySeverity(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    data = {severity: count for severity, count in rows} if rows else {}
    return JsonResponse({'ok': True})


def map_station(request):
    fireStations = FireStation.objects.values('name', 'latitude', 'longitude')

    fireStations_list = []

    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])
        fireStations_list.append(fs)

    context = {
        'fireStations': fireStations_list,
    }
    return render(request, 'map_station.html', context)
