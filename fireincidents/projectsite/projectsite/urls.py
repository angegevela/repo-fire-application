from django.contrib import admin
from django.urls import path

from fire.views import HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth, MultilineIncidentTop3Country, multiBarbySeverity, DoughnutChart, RadarChart, BubbleChart, barChart
from fire.views import FireTruckListView, FireTruckCreateView, FireTruckUpdateView, FireTruckDeleteView, FireFightersCreateView,FireFightersListView, FireFightersDeleteView, FireFightersUpdateView, IncidentListView, IncidentCreateView, IncidentUpdateView, IncidentDeleteView, LocationListView, LocationCreateView, LocationUpdateView, LocationDeleteView, WeatherConditionListView, WeatherConditionCreateView, WeatherConditionUpdateView, WeatherConditionDeleteView, FireStationListView, FireStationCreateView, FireStationUpdateView, FireStationDeleteView
from fire import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-chart'),
    path('chart/', PieCountbySeverity, name='chart'),
    path('lineChart/', LineCountbyMonth, name='line-chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', multiBarbySeverity, name='chart'),
    path('doughnut/', DoughnutChart, name='chart'),

    path('radar/', RadarChart, name='chart'),
    path('bubble/', BubbleChart, name='chart'),
    path('barChart', barChart, name='chart'),








    path('stations', views.map_station, name='map-station'),
    path('fire-incidents/', views.map_incidents, name='map-incidents'),
    #CRUD PATHS
    #Fire Trucks
    path('firetrucks/', FireTruckListView.as_view(), name='firetruck_list'),
    path('firetrucks/add/', FireTruckCreateView.as_view(), name='firetruck_add'),
    path('firetrucks/edit/<int:pk>/', FireTruckUpdateView.as_view(), name='firetruck_update'),
    path('firetrucks/delete/<int:pk>/', FireTruckDeleteView.as_view(), name='firetruck_delete'),
    #FireFighters
        path('firefighters/', FireFightersListView.as_view(), name='firefighters_list'),
    path('firefighters/add/', FireFightersCreateView.as_view(), name='firefighters_add'),
    path('firefighters/edit/<int:pk>/', FireFightersUpdateView.as_view(), name='firefighters_update'),
    path('firefighters/delete/<int:pk>/', FireFightersDeleteView.as_view(), name='firefighters_delete'),


    #Incidents
    path('Incidents/', IncidentListView.as_view(), name='incidents_list'),
    path('Incidents/add/',  IncidentCreateView.as_view(), name='incidents_add'),
    path('Incidents/edit/<int:pk>/', IncidentUpdateView.as_view(), name='incidents_update'),
    path('Incidents/delete/<int:pk>/', IncidentDeleteView.as_view(), name='incidents_delete'),
    #Location
    path('location/', LocationListView.as_view(), name='location_list'),
    path('location/add/',  LocationCreateView.as_view(), name='location_add'),
    path('location/edit/<int:pk>/', LocationUpdateView.as_view(), name='location_update'),
    path('location/delete/<int:pk>/', LocationDeleteView.as_view(), name='location_delete'),
    #Weather Condition
    path('weatherconditions/', WeatherConditionListView.as_view(), name='weathercondition_list'),
    path('weatherconditions/add/',  WeatherConditionCreateView.as_view(), name='weathercondition_add'),
    path('weatherconditions/edit/<int:pk>/', WeatherConditionUpdateView.as_view(), name='weathercondition_update'),
    path('weatherconditions/delete/<int:pk>/', WeatherConditionDeleteView.as_view(), name='weathercondition_delete'),
    #Fire Stations
    path('firestation/',FireStationListView.as_view(), name='firestation_list'),
    path('firestation/add/',  FireStationCreateView.as_view(), name='firestation_add'),
    path('firestation/edit/<int:pk>/', FireStationUpdateView.as_view(), name='firestation_update'),
    path('firestation/delete/<int:pk>/', FireStationDeleteView.as_view(), name='firestation_delete'),
]
