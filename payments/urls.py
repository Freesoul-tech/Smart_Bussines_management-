from django.urls import path

from .views import (
    payment_add,
    payment_edit,
    payment_list,
)


urlpatterns = [
    path(
        "",
        payment_list,
        name="payment_list",
    ),

    path(
        "add/",
        payment_add,
        name="payment_add",
    ),

    path(
        "<int:payment_id>/edit/",
        payment_edit,
        name="payment_edit",
    ),
]