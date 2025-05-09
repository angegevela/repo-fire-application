from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Locations, Incident, FireStation, FireTruck, Firefighters, WeatherConditions

from .forms import FireTruckForm,FireFightersForm, IncidentForm, LocationsForm, WheatherConditionsForm, FireStationForm
from django.urls import reverse_lazy
from django.contrib import messages
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

def LineCountbyMonth(request):
    current_year = datetime.now().year

    result = {month: 0 for month in range(1, 13)}
    
    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .values_list('date_time', flat=True)
    
    # Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    # If you want to convert month numbers to month names, you can use a dictionary mapping
    months_name = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    # Creating the result with month names instead of numbers
    result_with_month_names = {
        months_name[month]: count for month, count in result.items()
    }

    return JsonResponse(result_with_month_names)



def MultilineIncidentTop3Country(request):
    query = '''
    SELECT 
        fl.country,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN
        fire_locations fl ON fi.location_id = fl.id
    WHERE
        fl.country IN (
            SELECT
                fl_top.country
            FROM
                fire_incident fi_top
            JOIN
                fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY
                fl_top.country
            ORDER BY
                COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY
        fl.country, month
    ORDER BY
        fl.country, month;
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Initialize a dictionary to store the result
    result = {}

    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {m: 0 for m in months}

        # Update the incident count for the corresponding month
        result[country][month] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {m: 0 for m in months}

    # Sort months for each country
    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)

def multiBarbySeverity(request):
    query = '''
    SELECT
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM
        fire_incident fi
    GROUP BY fi.severity_level, month
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        level = str(row[0])
        month = row[1]
        total_incidents = row[2]

        if level not in result:
            result[level] = {month: 0 for month in months}
        result[level] [month] = total_incidents

    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items()))
    return JsonResponse(result)

def DoughnutChart(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    labels = []
    data = []
    background_colors = ["#1f353d", "#f1a648", "#1fda73", "#fa709a"]  # Expand if more levels

    for i, (severity, count) in enumerate(rows):
        labels.append(severity)
        data.append(count)

    chart_data = {
        "labels": labels,
        "datasets": [{
            "data": data,
            "backgroundColor": background_colors[:len(labels)]
        }]
    }

    return JsonResponse(chart_data)

def RadarChart(request):
    # Simulated categories and values
    categories = ["Rescue", "Suppression", "Evacuation", "Drills", "Investigation"]
    team1_data = [20, 25, 15, 10, 30]
    team2_data = [15, 20, 20, 15, 25]

    data = {
        "labels": categories,
        "datasets": [
            {
                "label": "Team A",
                "data": team1_data,
                "borderColor": "#1f7daf",
                "backgroundColor": "rgba(29, 122, 243, 0.25)",
                "pointBackgroundColor": "#1f7daf"
            },
            {
                "label": "Team B",
                "data": team2_data,
                "borderColor": "#71f6ac",
                "backgroundColor": "rgba(113, 246, 172, 0.25)",
                "pointBackgroundColor": "#71f6ac"
            }
        ]
    }
    return JsonResponse(data)
def BubbleChart(request):
    # Simulated data; replace with actual queries if applicable
    data = {
        "datasets": [
            {
                "label": "Cars",
                "data": [
                    {"x": 10, "y": 20, "r": 15},
                    {"x": 15, "y": 10, "r": 20},
                    {"x": 20, "y": 30, "r": 25}
                ],
                "backgroundColor": "#71c7ca"
            },
            {
                "label": "Motorcycles",
                "data": [
                    {"x": 5, "y": 15, "r": 10},
                    {"x": 25, "y": 10, "r": 18},
                    {"x": 30, "y": 25, "r": 22}
                ],
                "backgroundColor": "#1df3f3"
            }
        ]
    }
    return JsonResponse(data)


def barChart(request):
    data = {
        "labels": [
            "Jan", "Feb", "Mar", "Apr",
            "May", "Jun", "Jul", "Aug",
            "Sep", "Oct", "Nov", "Dec"
        ],
        "data": [12, 9, 15, 20, 14, 17, 22, 19, 13, 11, 16, 18]  
    }
    return JsonResponse(data)

#fire incident code view
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

def map_incidents(request):
    incidents = Incident.objects.select_related('location').all()
    locations = [
        {
            'latitude': str(incident.location.latitude),
            'longitude': str(incident.location.longitude),
            'severity': incident.severity_level,
            'description': incident.description,
        }
        for incident in incidents
        if incident.location.latitude and incident.location.longitude
    ]
    return render(request, 'map_incidents.html', {'locations': locations})

#CRUD CODES

class FireTruckListView(ListView):
    model = FireTruck
    template_name = 'firetruck_list.html'
    context_object_name = 'firetrucks'
    paginate_by = '3'


class FireTruckCreateView(CreateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck_add.html'
    success_url = reverse_lazy('firetruck_list')


class FireTruckUpdateView(UpdateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck_edit.html'
    success_url = reverse_lazy('firetruck_list')


class FireTruckDeleteView(DeleteView):
    model = FireTruck
    template_name = 'firetruck_del.html'
    success_url = reverse_lazy('firetruck_list')


#firefighters
class FireFightersListView(ListView):
    model = Firefighters
    template_name = 'firefighters_list.html'
    success_url = reverse_lazy('firefigthers_list')

class FireFightersCreateView(CreateView):
    model = Firefighters
    form_class = FireFightersForm
    template_name = 'firefighters_add.html'
    success_url = reverse_lazy('firefigthers_list')


class FireFightersUpdateView(UpdateView):
    model = Firefighters
    form_class = FireFightersForm
    template_name = 'firefigthers_edit.html'
    success_url = reverse_lazy('firefirefigthers_list')


class FireFightersDeleteView(DeleteView):
    model = Firefighters
    template_name = 'firefighters_del.html'
    success_url = reverse_lazy('firefigthers_list')

#Incidents
class IncidentListView(ListView):
    model = Incident
    template_name = 'incident_list.html'
    context_object_name = 'incidents'
class IncidentCreateView(CreateView):
    model = Incident
    form_class = IncidentForm 
    template_name = 'incident_add.html'
    success_url = reverse_lazy('incidents_list')

    def form_valid(self, form):
        messages.success(self.request, 'Incident successfully created.')
        return super().form_valid(form)

class IncidentUpdateView(UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident_edit.html'
    success_url = reverse_lazy('incidents_list')

    def form_valid(self, form):
        messages.success(self.request, 'Incident successfully updated.')
        return super().form_valid(form)

class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = 'incident_del.html'
    success_url = reverse_lazy('incidents_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Incident successfully deleted.')
        return super().delete(request, *args, **kwargs)


#Locations
class LocationListView(ListView):
    model = Locations
    template_name = 'location_list.html'
    context_object_name = 'locations'

class LocationCreateView(CreateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'location_add.html'
    success_url = reverse_lazy('location_list')

class LocationUpdateView(UpdateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'location_edit.html'
    success_url = reverse_lazy('location_list')

class LocationDeleteView(DeleteView):
    model =  Locations
    template_name = 'location_del.html'
    success_url = reverse_lazy('location_list')


#Fire Station
class FireStationListView(ListView):
    model = FireStation
    template_name = 'firestation_list.html'
    context_object_name = 'firestations'

class FireStationCreateView(CreateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation_add.html'
    success_url = reverse_lazy('firestation_list')

class FireStationUpdateView(UpdateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation_edit.html'
    success_url = reverse_lazy('firestation_list')

class FireStationDeleteView(DeleteView):
    model = FireStation
    template_name = 'firestation_del.html'
    success_url = reverse_lazy('firestation_list')

#Weather Conditions
class WeatherConditionListView(ListView):
    model = WeatherConditions
    template_name = 'weathercondition_list.html'
    context_object_name = 'weatherconditions'

class WeatherConditionCreateView(CreateView):
    model = WeatherConditions
    form_class = WheatherConditionsForm
    template_name = 'weathercondition_add.html'
    success_url = reverse_lazy('location_list')

class WeatherConditionUpdateView(UpdateView):
    model = WeatherConditions
    form_class = WheatherConditionsForm
    template_name = 'weathercondition_edit.html'
    success_url = reverse_lazy('location_list')

class WeatherConditionDeleteView(DeleteView):
    model = WeatherConditions
    template_name = 'weathercondition_del.html'
    success_url = reverse_lazy('location_list')



