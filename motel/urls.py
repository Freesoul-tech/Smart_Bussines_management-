from django.urls import path

from .views import (
    dashboard,
    parking_add,
    parking_list,
    quick_check_in,
    quick_check_out,
    vehicle_add,
    vehicle_check_in,
    vehicle_check_out,
    vehicle_list,
)

app_name = "motel"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("vehicles/", vehicle_list, name="vehicles"),
    path("vehicles/add/", vehicle_add, name="vehicle_add"),
    path("vehicles/<int:vehicle_id>/check-in/", vehicle_check_in, name="vehicle_check_in"),
    path("vehicles/<int:vehicle_id>/check-out/", vehicle_check_out, name="vehicle_check_out"),
    path("parking/", parking_list, name="parking"),
    path("parking/add/", parking_add, name="parking_add"),
    path("reservations/<int:reservation_id>/check-in/", quick_check_in, name="quick_check_in"),
    path("reservations/<int:reservation_id>/check-out/", quick_check_out, name="quick_check_out"),
]
