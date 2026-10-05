from django.urls import path

from .views import room_add, room_list


urlpatterns = [
    path("", room_list, name="room_list"),
    path("add/", room_add, name="room_add"),
]