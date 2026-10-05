from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from businesses.models import Business
from core.access import business_permission_required, get_user_business
from reservations.models import Reservation

from .forms import RoomForm
from .models import Room


def sync_room_status(room):

    if Reservation.objects.filter(
        room=room,
        status="checked_in",
    ).exists():

        new_status = "occupied"

    elif Reservation.objects.filter(
        room=room,
        status="confirmed",
    ).exists():

        new_status = "reserved"

    else:

        new_status = "available"

    if room.status != new_status:

        room.status = new_status

        room.save(
            update_fields=["status"]
        )


@login_required
@business_permission_required("rooms.view_room")
def room_list(request):

    business = get_user_business(request.user)

    if not business:

        return redirect(
            "business_setup"
        )

    rooms = Room.objects.filter(
        business=business
    )

    # Synchronize every room with
    # its current reservations.
    for room in rooms:

        sync_room_status(room)

    return render(
        request,
        "rooms/room_list.html",
        {
            "business": business,
            "rooms": rooms,

            # Shared dashboard layout
            "active_page": "rooms",

            # Business model
            "business_model_name":
                business.get_business_model_display(),

            # Sidebar business category
            "is_accommodation":
                business.business_model in {
                    "hotel",
                    "motel",
                    "lodge",
                    "guest_house",
                },

            "is_food_business":
                business.business_model in {
                    "restaurant",
                    "bakery",
                },

            "is_pub_bar":
                business.business_model == "pub_bar",

            "is_boutique":
                business.business_model == "boutique",
        },
    )


@login_required
@business_permission_required("rooms.add_room")
def room_add(request):

    business = get_user_business(request.user)

    if not business:

        return redirect(
            "business_setup"
        )

    if request.method == "POST":

        form = RoomForm(
            request.POST
        )

        if form.is_valid():

            room = form.save(
                commit=False
            )

            room.business = business

            room.save()

            return redirect(
                "room_list"
            )

    else:

        form = RoomForm()

    return render(
        request,
        "rooms/room_form.html",
        {
            "form": form,
            "business": business,
        },
    )
