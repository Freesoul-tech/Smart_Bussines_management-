from django.urls import path

from .views import (
    customer_list,
    customer_add,
    customer_edit,
    customer_detail,
)

app_name = "customers"

urlpatterns = [
    path("", customer_list, name="customer_list"),

    path("add/", customer_add, name="customer_add"),

    path(
        "<int:customer_id>/",
        customer_detail,
        name="customer_detail",
    ),

    path(
        "<int:customer_id>/edit/",
        customer_edit,
        name="customer_edit",
    ),
]