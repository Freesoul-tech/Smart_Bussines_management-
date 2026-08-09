from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('guests/', views.guests, name='guests'),
    path('reservations/', views.reservations, name='reservations'),
    path('housekeeping/', views.housekeeping, name='housekeeping'),
    path('billing/', views.billing, name='billing'),
    path('reports-analytics/', views.reports_analytics, name='reports-analytics'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.settings, name='settings'),
]
