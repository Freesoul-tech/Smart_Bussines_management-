from django.urls import path

from .views import (
    employee_add,
    employee_deactivate,
    employee_edit,
    employee_list,
)


urlpatterns = [
    path("", employee_list, name="employee_list"),

    path(
        "add/",
        employee_add,
        name="employee_add",
    ),

    path(
        "<int:employee_id>/edit/",
        employee_edit,
        name="employee_edit",
    ),

    path(
        "<int:employee_id>/deactivate/",
        employee_deactivate,
        name="employee_deactivate",
    ),
]