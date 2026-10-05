from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render

from businesses.models import Business
from core.access import get_user_business
from customers.models import Customer
from employees.models import Employee
from payments.models import Payment
from reservations.models import Reservation
from rooms.models import Room


BUSINESS_MODEL_NAMES = {
    "hotel": "Hotel",
    "motel": "Motel",
    "lodge": "Lodge",
    "guest_house": "Guest House",
    "restaurant": "Restaurant",
    "bakery": "Bakery",
    "pub_bar": "Pub / Bar",
    "boutique": "Boutique",
}


@login_required
def dashboard(request):

    # =================================================
    # USER BUSINESS
    # =================================================

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    # =================================================
    # BUSINESS MODEL
    # =================================================

    business_model = business.business_model or ""

    business_model_name = BUSINESS_MODEL_NAMES.get(
        business_model,
        "Business",
    )

    # =================================================
    # BUSINESS MODEL FLAGS
    # =================================================

    is_accommodation = business_model in [
        "hotel",
        "motel",
        "lodge",
        "guest_house",
    ]

    is_food_business = business_model in [
        "restaurant",
        "bakery",
    ]

    is_pub_bar = business_model == "pub_bar"

    is_boutique = business_model == "boutique"

    # =================================================
    # ROOMS
    # =================================================

    rooms = Room.objects.filter(
        business=business
    )

    total_rooms = rooms.count()

    available_rooms = rooms.filter(
        status="available"
    ).count()

    occupied_rooms = rooms.filter(
        status="occupied"
    ).count()

    reserved_rooms = rooms.filter(
        status="reserved"
    ).count()

    maintenance_rooms = rooms.filter(
        status="maintenance"
    ).count()

    inactive_rooms = rooms.filter(
        status="inactive"
    ).count()

    # =================================================
    # RESERVATIONS
    # =================================================

    reservations = Reservation.objects.filter(
        business=business
    )

    total_reservations = reservations.count()

    active_reservations = reservations.exclude(
        status="cancelled"
    ).count()

    cancelled_reservations = reservations.filter(
        status="cancelled"
    ).count()

    confirmed_reservations = reservations.filter(
        status="confirmed"
    ).count()

    checked_in_reservations = reservations.filter(
        status="checked_in"
    ).count()

    checked_out_reservations = reservations.filter(
        status="checked_out"
    ).count()

    # =================================================
    # PAYMENTS
    # =================================================

    payments = Payment.objects.filter(
        business=business
    )

    total_paid = (
        payments.filter(
            status="paid"
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    total_refunded = (
        payments.filter(
            status="refunded"
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    pending_payments = (
        payments.filter(
            status="pending"
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    # =================================================
    # EMPLOYEES
    # =================================================

    employees = Employee.objects.filter(
        business=business
    )

    total_employees = employees.count()

    active_employees = employees.filter(
        employment_status="active"
    ).count()

    inactive_employees = employees.exclude(
        employment_status="active"
    ).count()

    # =================================================
    # CUSTOMERS
    # =================================================

    customers = Customer.objects.filter(
        business=business
    )

    total_customers = customers.count()

    # =================================================
    # RECENT RESERVATIONS
    # =================================================

    recent_reservations = (
        reservations
        .select_related(
            "room",
            "customer",
        )
        .order_by("-created_at")[:5]
    )

    # =================================================
    # RECENT PAYMENTS
    # =================================================

    recent_payments = (
        payments
        .select_related(
            "reservation",
            "reservation__room",
            "reservation__customer",
        )
        .order_by("-created_at")[:5]
    )

    # =================================================
    # OCCUPANCY
    # =================================================

    if total_rooms > 0:

        occupancy_rate = round(
            (
                occupied_rooms
                / total_rooms
            )
            * 100,
            1,
        )

    else:

        occupancy_rate = 0

    # =================================================
    # CONTEXT
    # =================================================

    context = {

        # ---------------------------------------------
        # BUSINESS
        # ---------------------------------------------

        "business": business,
        "business_model": business_model,
        "business_model_name": business_model_name,

        # ---------------------------------------------
        # BUSINESS MODEL FLAGS
        # ---------------------------------------------

        "is_accommodation": is_accommodation,
        "is_food_business": is_food_business,
        "is_pub_bar": is_pub_bar,
        "is_boutique": is_boutique,

        # ---------------------------------------------
        # ROOMS
        # ---------------------------------------------

        "total_rooms": total_rooms,
        "available_rooms": available_rooms,
        "occupied_rooms": occupied_rooms,
        "reserved_rooms": reserved_rooms,
        "maintenance_rooms": maintenance_rooms,
        "inactive_rooms": inactive_rooms,

        # ---------------------------------------------
        # RESERVATIONS
        # ---------------------------------------------

        "total_reservations": total_reservations,
        "active_reservations": active_reservations,
        "cancelled_reservations": cancelled_reservations,
        "confirmed_reservations": confirmed_reservations,
        "checked_in_reservations": checked_in_reservations,
        "checked_out_reservations": checked_out_reservations,

        # ---------------------------------------------
        # PAYMENTS
        # ---------------------------------------------

        "total_paid": total_paid,
        "total_refunded": total_refunded,
        "pending_payments": pending_payments,

        # ---------------------------------------------
        # EMPLOYEES
        # ---------------------------------------------

        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,

        # ---------------------------------------------
        # CUSTOMERS
        # ---------------------------------------------

        "total_customers": total_customers,

        # ---------------------------------------------
        # OCCUPANCY
        # ---------------------------------------------

        "occupancy_rate": occupancy_rate,

        # ---------------------------------------------
        # RECENT DATA
        # ---------------------------------------------

        "recent_reservations": recent_reservations,
        "recent_payments": recent_payments,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )