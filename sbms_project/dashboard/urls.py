from django.urls import path
from .views import (
    billing,
    delete_account,
    guests,
    housekeeping,
    index,
    landing,
    login_view,
    logout_view,
    notifications,
    register_view,
    reports_analytics,
    reservations,
    settings,
)

app_name = 'dashboard'

urlpatterns = [
    path('', landing, name='landing'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', index, name='index'),
    path('guests/', guests, name='guests'),
    path('reservations/', reservations, name='reservations'),
    path('housekeeping/', housekeeping, name='housekeeping'),
    path('billing/', billing, name='billing'),
    path('reports-analytics/', reports_analytics, name='reports-analytics'),
    path('notifications/', notifications, name='notifications'),
    path('settings/', settings, name='settings'),
    path('settings/delete-account/', delete_account, name='delete_account'),
]
