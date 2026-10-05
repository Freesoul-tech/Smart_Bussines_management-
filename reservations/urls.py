from django.urls import path

from .views import (
    reservation_add,
    reservation_cancel,
    reservation_check_in,
    reservation_check_out,
    reservation_confirm,
    reservation_edit,
    reservation_list,
)


urlpatterns = [

    path(
        "",
        reservation_list,
        name="reservation_list",
    ),

    path(
        "add/",
        reservation_add,
        name="reservation_add",
    ),

    path(
        "<int:reservation_id>/confirm/",
        reservation_confirm,
        name="reservation_confirm",
    ),

    path(
        "<int:reservation_id>/check-in/",
        reservation_check_in,
        name="reservation_check_in",
    ),

    path(
        "<int:reservation_id>/check-out/",
        reservation_check_out,
        name="reservation_check_out",
    ),

    path(
        "<int:reservation_id>/cancel/",
        reservation_cancel,
        name="reservation_cancel",
    ),

    path(
        "<int:reservation_id>/edit/",
        reservation_edit,
        name="reservation_edit",
    ),
]