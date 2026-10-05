from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.access import get_user_business
from reservations.models import Reservation
from rooms.models import Room

from .forms import ParkingSpaceForm, VehicleForm
from .models import ParkingSpace, Vehicle


def sync_room_status(room):
    if Reservation.objects.filter(room=room, status="checked_in").exists():
        room.status = "occupied"
    elif Reservation.objects.filter(room=room, status="confirmed").exists():
        room.status = "reserved"
    else:
        room.status = "available"
    room.save(update_fields=["status"])


def motel_business_required(view):
    def wrapped(request, *args, **kwargs):
        business = get_user_business(request.user)
        if not business or business.business_model != "motel":
            raise PermissionDenied
        if business.owner_id != request.user.id and not request.user.has_perm("motel.view_vehicle"):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    wrapped.__name__ = view.__name__
    wrapped.__doc__ = view.__doc__
    return wrapped


@login_required
@motel_business_required
def dashboard(request):
    business = get_user_business(request.user)
    today = timezone.localdate()
    reservations = Reservation.objects.filter(business=business).select_related("room", "customer")
    rooms = Room.objects.filter(business=business)
    vehicles = Vehicle.objects.filter(business=business)
    parking_spaces = ParkingSpace.objects.filter(business=business).select_related("current_vehicle")
    context = {
        "business": business,
        "business_model_name": "Motel",
        "active_page": "motel",
        "available_rooms": rooms.filter(status="available").count(),
        "occupied_rooms": rooms.filter(status="occupied").count(),
        "arrivals_today": reservations.filter(check_in=today, status__in=["pending", "confirmed"]),
        "departures_today": reservations.filter(check_out=today, status="checked_in"),
        "parking_available": parking_spaces.filter(status="available", current_vehicle__isnull=True).count(),
        "vehicles_checked_in": vehicles.filter(is_checked_in=True).count(),
        "parking_spaces": parking_spaces,
    }
    return render(request, "motel/dashboard.html", context)


@login_required
@motel_business_required
def vehicle_list(request):
    business = get_user_business(request.user)
    vehicles = Vehicle.objects.filter(business=business).select_related("customer", "reservation", "parking_space")
    parking_spaces = ParkingSpace.objects.filter(business=business, status="available", current_vehicle__isnull=True)
    return render(request, "motel/vehicle_list.html", {"business": business, "vehicles": vehicles, "parking_spaces": parking_spaces, "active_page": "motel"})


@login_required
@motel_business_required
def vehicle_add(request):
    business = get_user_business(request.user)
    form = VehicleForm(request.POST or None, business=business)
    form.business = business
    if request.method == "POST" and form.is_valid():
        vehicle = form.save(commit=False)
        vehicle.business = business
        vehicle.save()
        return redirect("motel:vehicles")
    return render(request, "motel/vehicle_form.html", {"business": business, "form": form, "active_page": "motel"})


@login_required
@motel_business_required
def parking_list(request):
    business = get_user_business(request.user)
    spaces = ParkingSpace.objects.filter(business=business).select_related("current_vehicle")
    return render(request, "motel/parking_list.html", {"business": business, "spaces": spaces, "active_page": "motel"})


@login_required
@motel_business_required
def parking_add(request):
    business = get_user_business(request.user)
    form = ParkingSpaceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        space = form.save(commit=False)
        space.business = business
        space.save()
        return redirect("motel:parking")
    return render(request, "motel/parking_form.html", {"business": business, "form": form, "active_page": "motel"})


@login_required
@motel_business_required
def quick_check_in(request, reservation_id):
    if request.method != "POST":
        return redirect("motel:dashboard")
    business = get_user_business(request.user)
    reservation = get_object_or_404(Reservation, id=reservation_id, business=business)
    if reservation.status == "confirmed":
        reservation.status = "checked_in"
        reservation.save(update_fields=["status", "updated_at"])
        sync_room_status(reservation.room)
    return redirect("motel:dashboard")


@login_required
@motel_business_required
def quick_check_out(request, reservation_id):
    if request.method != "POST":
        return redirect("motel:dashboard")
    business = get_user_business(request.user)
    reservation = get_object_or_404(Reservation, id=reservation_id, business=business)
    if reservation.status == "checked_in":
        with transaction.atomic():
            reservation.status = "checked_out"
            reservation.save(update_fields=["status", "updated_at"])
            sync_room_status(reservation.room)
            Vehicle.objects.filter(reservation=reservation, business=business).update(
                is_checked_in=False, checked_out_at=timezone.now()
            )
            ParkingSpace.objects.filter(current_vehicle__reservation=reservation, business=business).update(
                current_vehicle=None, assigned_at=None
            )
    return redirect("motel:dashboard")


@login_required
@motel_business_required
def vehicle_check_in(request, vehicle_id):
    if request.method != "POST":
        return redirect("motel:vehicles")
    business = get_user_business(request.user)
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, business=business)
    space = get_object_or_404(
        ParkingSpace,
        id=request.POST.get("parking_space"),
        business=business,
        status="available",
        current_vehicle__isnull=True,
    )
    with transaction.atomic():
        vehicle.is_checked_in = True
        vehicle.checked_in_at = timezone.now()
        vehicle.checked_out_at = None
        vehicle.save(update_fields=["is_checked_in", "checked_in_at", "checked_out_at"])
        space.current_vehicle = vehicle
        space.assigned_at = timezone.now()
        space.save(update_fields=["current_vehicle", "assigned_at"])
    return redirect("motel:vehicles")


@login_required
@motel_business_required
def vehicle_check_out(request, vehicle_id):
    if request.method != "POST":
        return redirect("motel:vehicles")
    business = get_user_business(request.user)
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, business=business)
    with transaction.atomic():
        vehicle.is_checked_in = False
        vehicle.checked_out_at = timezone.now()
        vehicle.save(update_fields=["is_checked_in", "checked_out_at"])
        ParkingSpace.objects.filter(current_vehicle=vehicle, business=business).update(
            current_vehicle=None, assigned_at=None
        )
    return redirect("motel:vehicles")
