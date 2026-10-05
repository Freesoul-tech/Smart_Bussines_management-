from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from core.access import get_user_business
from reservations.models import Reservation
from rooms.models import Room

from .forms import LodgeActivityForm, LodgePackageForm
from .models import LodgeActivity, LodgePackage, LodgeUnit


def lodge_business_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        business = get_user_business(request.user)
        if not business or business.business_model != "lodge":
            raise PermissionDenied
        if business.owner_id != request.user.id and not request.user.has_perm("lodge.view_lodgeunit"):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapped


@login_required
@lodge_business_required
def dashboard(request):
    business = get_user_business(request.user)
    today = __import__("django.utils.timezone", fromlist=["localdate"]).localdate()
    rooms = Room.objects.filter(business=business)
    reservations = Reservation.objects.filter(business=business).select_related("room", "customer")
    units = LodgeUnit.objects.filter(business=business, is_active=True).select_related("room")
    context = {
        "business": business,
        "business_model_name": "Lodge",
        "active_page": "lodge",
        "total_units": units.count(),
        "cabins": units.filter(unit_type="cabin").count(),
        "chalets": units.filter(unit_type="chalet").count(),
        "occupied_units": rooms.filter(status="occupied").count(),
        "available_units": rooms.filter(status="available").count(),
        "arrivals_today": reservations.filter(check_in=today, status__in=["pending", "confirmed"]),
        "departures_today": reservations.filter(check_out=today, status="checked_in"),
        "activities": LodgeActivity.objects.filter(business=business, is_active=True),
        "packages": LodgePackage.objects.filter(business=business, is_active=True).prefetch_related("included_activities"),
    }
    return render(request, "lodge/dashboard.html", context)


@login_required
@lodge_business_required
def activity_list(request):
    business = get_user_business(request.user)
    activities = LodgeActivity.objects.filter(business=business)
    return render(request, "lodge/activity_list.html", {"business": business, "activities": activities, "active_page": "lodge"})


@login_required
@lodge_business_required
def activity_add(request):
    business = get_user_business(request.user)
    form = LodgeActivityForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        activity = form.save(commit=False)
        activity.business = business
        activity.save()
        return redirect("lodge:activities")
    return render(request, "lodge/activity_form.html", {"business": business, "form": form, "active_page": "lodge"})


@login_required
@lodge_business_required
def package_list(request):
    business = get_user_business(request.user)
    packages = LodgePackage.objects.filter(business=business).prefetch_related("included_activities")
    return render(request, "lodge/package_list.html", {"business": business, "packages": packages, "active_page": "lodge"})


@login_required
@lodge_business_required
def package_add(request):
    business = get_user_business(request.user)
    form = LodgePackageForm(request.POST or None, business=business)
    if request.method == "POST" and form.is_valid():
        package = form.save(commit=False)
        package.business = business
        package.save()
        form.save_m2m()
        return redirect("lodge:packages")
    return render(request, "lodge/package_form.html", {"business": business, "form": form, "active_page": "lodge"})
