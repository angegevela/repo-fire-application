from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Locations, Incident, FireStation, FireTruck, Firefighters, WeatherConditions

from .forms import FireTruckForm,FireFightersForm, IncidentForm, LocationsForm, WheatherConditionsForm, FireStationForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth

from collections import defaultdict
import calendar


from django.db.models import Q
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
    
    if rows:
        data = {severity_level: count for severity_level, count in rows} if rows else {}
    else:
        data = {}
    return JsonResponse(data)

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
     # Count incidents grouped by location
    location_data = Incident.objects.values(
        'location__latitude',
        'location__longitude',
        'location__name'
    ).annotate(
        count=Count('id')
    ).exclude(
        location__latitude__isnull=True,
        location__longitude__isnull=True
    )

    dataset = []

    for loc in location_data:
        dataset.append({
            "x": float(loc['location__longitude']),
            "y": float(loc['location__latitude']),
            "r": loc['count'],  # Bubble radius
            "label": loc['location__name']
        })

    response_data = {
        "datasets": [
            {
                "label": "Incidents per Location",
                "data": dataset,
                "backgroundColor": "#f39c12"
            }
        ]
    }
    return JsonResponse(response_data)
def barChart(request):
    query = '''
    SELECT
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM
        fire_incident fi
    GROUP BY month
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Map month numbers to month names
    month_map = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }

    month_labels = [month_map[str(i).zfill(2)] for i in range(1, 13)]
    data = {str(i).zfill(2): 0 for i in range(1, 13)}
    
    for row in rows:
        month = row[0]
        count = row[1]
        data[month] = count

    return JsonResponse({
        "labels": month_labels,          
        "data": [data[m] for m in sorted(data.keys())]  
    })

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
    paginate_by = 3

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return FireTruck.objects.filter(
                Q(truck_number__icontains=query) |
                Q(model__icontains=query) |
                Q(station__name__icontains=query)
            ).select_related('station')
        return FireTruck.objects.all().select_related('station')



class FireTruckCreateView(CreateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck_add.html'
    success_url = reverse_lazy('firetruck_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'FireTruck details successfully created.')
        return super().form_valid(form)


class FireTruckUpdateView(UpdateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck_edit.html'
    success_url = reverse_lazy('firetruck_list')
    def form_valid(self, form):
        messages.success(self.request, 'FireTruck details successfully updated.')
        return super().form_valid(form)


class FireTruckDeleteView(DeleteView):
    model = FireTruck
    template_name = 'firetruck_del.html'
    success_url = reverse_lazy('firetruck_list')
    
    def get_success_url(self):
        messages.success(self.request, 'FireTruck successfully deleted.')
        return reverse_lazy('incidents_list')


#firefighters
class FireFightersListView(ListView):
    model = Firefighters
    template_name = 'firefighters_list.html'
    context_object_name = 'firefighters'
    paginate_by = 5

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            object_list = Firefighters.objects.filter(
                Q(name__icontains=query) |
                Q(rank__icontains=query) |
                Q(experience_level__icontains=query) |
                Q(station__icontains=query)
            )
        else:
            object_list = Firefighters.objects.all()
        return object_list

class FireFightersCreateView(CreateView):
    model = Firefighters
    form_class = FireFightersForm
    template_name = 'firefighters_add.html'
    success_url = reverse_lazy('firefighters_list')

    def form_valid(self, form):
        messages.success(self.request, 'Firefighter successfully added.')
        return super().form_valid(form)


class FireFightersUpdateView(UpdateView):
    model = Firefighters
    form_class = FireFightersForm
    template_name = 'firefighter_edit.html'
    success_url = reverse_lazy('firefighters_list')

    def form_valid(self, form):
        messages.success(self.request, 'Firefighter details updated.')
        return super().form_valid(form)


class FireFightersDeleteView(DeleteView):
    model = Firefighters
    template_name = 'firefighters_del.html'
    success_url = reverse_lazy('firefighters_list')

    def get_success_url(self):
        messages.success(self.request, 'FireFighters details successfully deleted.')
        return reverse_lazy('incidents_list')

#Incidents
class IncidentListView(ListView):
    model = Incident
    template_name = 'incident_list.html'
    context_object_name = 'incidents'

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return Incident.objects.filter(
                Q(severity_level__icontains=query) |
                Q(description__icontains=query) |
                Q(location__name__icontains=query)
            ).select_related('location')
        return Incident.objects.all().select_related('location')

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

    def get_success_url(self):
        messages.success(self.request, 'Incident details successfully deleted.')
        return reverse_lazy('incidents_list')



#Locations
class LocationListView(ListView):
    model = Locations
    template_name = 'location_list.html'
    context_object_name = 'locations'

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return Locations.objects.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query)
            )
        return Locations.objects.all()

class LocationCreateView(CreateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'location_add.html'
    success_url = reverse_lazy('location_list')
    def form_valid(self, form):
        messages.success(self.request, 'Location successfully created.')
        return super().form_valid(form)

class LocationUpdateView(UpdateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'location_edit.html'
    success_url = reverse_lazy('location_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Location details successfully updated.')
        return super().form_valid(form)

class LocationDeleteView(DeleteView):
    model =  Locations
    template_name = 'location_del.html'
    success_url = reverse_lazy('location_list')
    def get_success_url(self):
        messages.success(self.request, 'Location details successfully deleted.')
        return reverse_lazy('incidents_list')


#Fire Station
class FireStationListView(ListView):
    model = FireStation
    template_name = 'firestation_list.html'
    context_object_name = 'firestations'

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return FireStation.objects.filter(
                Q(name__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query)
            )
        return FireStation.objects.all()


class FireStationCreateView(CreateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation_add.html'
    success_url = reverse_lazy('firestation_list')
    def form_valid(self, form):
        messages.success(self.request, 'Firestation Details successfully created.')
        return super().form_valid(form)

class FireStationUpdateView(UpdateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation_edit.html'
    success_url = reverse_lazy('firestation_list')
    def form_valid(self, form):
        messages.success(self.request, 'Firestation details successfully updated.')
        return super().form_valid(form)

class FireStationDeleteView(DeleteView):
    model = FireStation
    template_name = 'firestation_del.html'
    success_url = reverse_lazy('firestation_list')
    def get_success_url(self):
        messages.success(self.request, 'Firestation Details successfully deleted.')
        return reverse_lazy('incidents_list')

#Weather Conditions
class WeatherConditionListView(ListView):
    model = WeatherConditions
    template_name = 'weathercondition_list.html'
    context_object_name = 'weatherconditions'

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return WeatherConditions.objects.filter(
                Q(temperature__icontains=query) |
                Q(humidity__icontains=query) |
                Q(wind_speed__icontains=query) |
                Q(weather_description__icontains=query)
            ).select_related('incident')
        return WeatherConditions.objects.all().select_related('incident')


class WeatherConditionCreateView(CreateView):
    model = WeatherConditions
    form_class = WheatherConditionsForm
    template_name = 'weathercondition_add.html'
    success_url = reverse_lazy('location_list')
    def form_valid(self, form):
        messages.success(self.request, 'Weather Conditions Details successfully created.')
        return super().form_valid(form)

class WeatherConditionUpdateView(UpdateView):
    model = WeatherConditions
    form_class = WheatherConditionsForm
    template_name = 'weathercondition_edit.html'
    success_url = reverse_lazy('location_list')
    def form_valid(self, form):
        messages.success(self.request, 'Weather Condition details successfully updated.')
        return super().form_valid(form)

class WeatherConditionDeleteView(DeleteView):
    model = WeatherConditions
    template_name = 'weathercondition_del.html'
    success_url = reverse_lazy('location_list')
    def get_success_url(self):
        messages.success(self.request, 'Weather Condition Details successfully deleted.')
        return reverse_lazy('incidents_list')



