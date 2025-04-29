from django.contrib import admin
from django.urls import path

from fire.views import HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth, MultilineIncidentTop3Country, multiBarbySeverity, DoughnutChart, RadarChart, BubbleChart, barChart
from fire.views import FireTruckListView, FireTruckCreateView, FireTruckUpdateView, FireTruckDeleteView
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
    path('firetrucks/', FireTruckListView.as_view(), name='firetruck_list'),
    path('firetrucks/add/', FireTruckCreateView.as_view(), name='firetruck_add'),
    path('firetrucks/edit/<int:pk>/', FireTruckUpdateView.as_view(), name='firetruck_update'),
    path('firetrucks/delete/<int:pk>/', FireTruckDeleteView.as_view(), name='firetruck_delete')




]
