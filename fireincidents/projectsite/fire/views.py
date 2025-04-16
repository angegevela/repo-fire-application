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

def LineCountbyMonth(request):
    current_year = datetime.now().year

    result = {month: 0 for  month in range(1, 13)}
    
    incidents_per_month = Incident.objects.filter(date_time__year = current_year) \
        .values_list('date_time', flat=True)
    
    #Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    # If you want to convert month numbers to month names, you can use a dictionary mapping
    months_name = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    
def LineCountbyMonth(request):
    # Manually set incidents per month
    result_with_month_name = {
        'Jan': 542,
        'Feb': 480,
        'Mar': 430,
        'Apr': 550,
        'May': 453,
        'Jun': 380,
        'Jul': 434,
        'Aug': 568,
        'Sep': 610,
        'Oct': 700,
        'Nov': 900,
        'Dec': 0
    }
    return JsonResponse({'data': result_with_month_name})

