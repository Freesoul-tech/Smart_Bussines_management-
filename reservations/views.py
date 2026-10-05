
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from businesses.models import Business
from core.access import business_permission_required, get_user_business
from rooms.models import Room

from .forms import ReservationForm
from .models import Reservation


def update_room_status(room):
    """
    Automatically update the room status based on reservations.
    """

    # A checked-in reservation means the room is occupied.
    if Reservation.objects.filter(
        room=room,
        status="checked_in",
    ).exists():

        new_status = "occupied"

    # A confirmed reservation means the room is reserved.
    elif Reservation.objects.filter(
        room=room,
        status="confirmed",
    ).exists():

        new_status = "reserved"

    # Otherwise the room is available.
    else:

        new_status = "available"

    if room.status != new_status:

        room.status = new_status

        room.save(
            update_fields=["status"]
        )


@login_required
@business_permission_required("reservations.view_reservation")
def reservation_list(request):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    reservations = (
        Reservation.objects.filter(
            business=business
        )
        .select_related(
            "room",
            "customer",
        )
    )

    return render(
        request,
        "reservations/reservation_list.html",
        {
            "business": business,
            "reservations": reservations,
        },
    )


@login_required
@business_permission_required("reservations.add_reservation")
def reservation_add(request):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    if request.method == "POST":

        form = ReservationForm(
            request.POST,
            business=business,
        )

        if form.is_valid():

            reservation = form.save(
                commit=False
            )

            # -------------------------------------------------
            # KEEP RESERVATION INSIDE USER'S BUSINESS
            # -------------------------------------------------

            reservation.business = business

            reservation.save()

            # -------------------------------------------------
            # UPDATE ROOM STATUS
            # -------------------------------------------------

            update_room_status(
                reservation.room
            )

            return redirect(
                "reservation_list"
            )

    else:

        form = ReservationForm(
            business=business,
        )

    return render(
        request,
        "reservations/reservation_form.html",
        {
            "form": form,
            "business": business,
            "page_title": "Add Reservation",
        },
    )


@login_required
@business_permission_required("reservations.change_reservation")
def reservation_confirm(
    request,
    reservation_id,
):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        business=business,
    )

    if request.method == "POST":

        reservation.status = "confirmed"

        reservation.save(
            update_fields=["status"]
        )

        update_room_status(
            reservation.room
        )

    return redirect(
        "reservation_list"
    )


@login_required
@business_permission_required("reservations.change_reservation")
def reservation_check_in(
    request,
    reservation_id,
):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        business=business,
    )

    if request.method == "POST":

        if reservation.status == "confirmed":

            reservation.status = "checked_in"

            reservation.save(
                update_fields=["status"]
            )

            update_room_status(
                reservation.room
            )

    return redirect(
        "reservation_list"
    )


@login_required
@business_permission_required("reservations.change_reservation")
def reservation_check_out(
    request,
    reservation_id,
):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        business=business,
    )

    if request.method == "POST":

        if reservation.status == "checked_in":

            reservation.status = "checked_out"

            reservation.save(
                update_fields=["status"]
            )

            update_room_status(
                reservation.room
            )

    return redirect(
        "reservation_list"
    )


@login_required
@business_permission_required("reservations.change_reservation")
def reservation_cancel(
    request,
    reservation_id,
):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        business=business,
    )

    if request.method == "POST":

        if reservation.status in [
            "pending",
            "confirmed",
        ]:

            reservation.status = "cancelled"

            reservation.save(
                update_fields=["status"]
            )

            update_room_status(
                reservation.room
            )

    return redirect(
        "reservation_list"
    )


@login_required
@business_permission_required("reservations.change_reservation")
def reservation_edit(
    request,
    reservation_id,
):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    reservation = get_object_or_404(
        Reservation.objects.select_related(
            "customer",
            "room",
        ),
        id=reservation_id,
        business=business,
    )

    old_room = reservation.room

    if request.method == "POST":

        form = ReservationForm(
            request.POST,
            instance=reservation,
            business=business,
        )

        if form.is_valid():

            reservation = form.save(
                commit=False
            )

            # -------------------------------------------------
            # KEEP SAME BUSINESS
            # -------------------------------------------------

            reservation.business = business

            reservation.save()

            # -------------------------------------------------
            # UPDATE NEW ROOM
            # -------------------------------------------------

            update_room_status(
                reservation.room
            )

            # -------------------------------------------------
            # UPDATE OLD ROOM IF ROOM CHANGED
            # -------------------------------------------------

            if old_room != reservation.room:

                update_room_status(
                    old_room
                )

            return redirect(
                "reservation_list"
            )

    else:

        form = ReservationForm(
            instance=reservation,
            business=business,
        )

    return render(
        request,
        "reservations/reservation_form.html",
        {
            "form": form,
            "business": business,
            "editing": True,
            "reservation": reservation,
            "page_title": "Edit Reservation",
        },
    )

