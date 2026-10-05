from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from businesses.models import Business
from core.access import get_user_business
from reservations.models import Reservation

from .forms import CustomerForm
from .models import Customer


@login_required
def customer_list(request):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    customers = Customer.objects.filter(
        business=business
    )

    # -------------------------------------------------
    # SEARCH
    # -------------------------------------------------

    search = request.GET.get(
        "search",
        "",
    ).strip()

    if search:

        customers = customers.filter(
            Q(name__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
        )

    # -------------------------------------------------
    # STATISTICS
    # -------------------------------------------------

    total_customers = Customer.objects.filter(
        business=business
    ).count()

    return render(
        request,
        "customers/customer_list.html",
        {
            "business": business,
            "customers": customers,
            "total_customers": total_customers,
            "search": search,
        },
    )


@login_required
def customer_add(request):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    if request.method == "POST":

        form = CustomerForm(
            request.POST
        )

        if form.is_valid():

            customer = form.save(
                commit=False
            )

            customer.business = business

            customer.save()

            return redirect(
                "customers:customer_detail",
                customer_id=customer.id,
            )

    else:

        form = CustomerForm()

    return render(
        request,
        "customers/customer_form.html",
        {
            "form": form,
            "business": business,
            "page_title": "Add Customer",
        },
    )


@login_required
def customer_edit(
    request,
    customer_id,
):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    customer = get_object_or_404(
        Customer,
        id=customer_id,
        business=business,
    )

    if request.method == "POST":

        form = CustomerForm(
            request.POST,
            instance=customer,
        )

        if form.is_valid():

            form.save()

            return redirect(
                "customers:customer_detail",
                customer_id=customer.id,
            )

    else:

        form = CustomerForm(
            instance=customer
        )

    return render(
        request,
        "customers/customer_form.html",
        {
            "form": form,
            "business": business,
            "customer": customer,
            "page_title": "Edit Customer",
            "editing": True,
        },
    )


@login_required
def customer_detail(
    request,
    customer_id,
):

    # -------------------------------------------------
    # GET USER'S BUSINESS
    # -------------------------------------------------

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    # -------------------------------------------------
    # GET CUSTOMER
    # -------------------------------------------------

    customer = get_object_or_404(
        Customer,
        id=customer_id,
        business=business,
    )

    # -------------------------------------------------
    # GET CUSTOMER RESERVATIONS
    # -------------------------------------------------

    reservations = (
        Reservation.objects.filter(
            business=business,
            customer=customer,
        )
        .select_related("room")
        .order_by(
            "-check_in",
            "-created_at",
        )
    )

    # -------------------------------------------------
    # RESERVATION STATISTICS
    # -------------------------------------------------

    total_reservations = reservations.count()

    active_reservations = reservations.exclude(
        status__in=[
            "cancelled",
            "checked_out",
        ]
    ).count()

    completed_reservations = reservations.filter(
        status="checked_out"
    ).count()

    cancelled_reservations = reservations.filter(
        status="cancelled"
    ).count()

    # -------------------------------------------------
    # TOTAL RESERVATION VALUE
    # -------------------------------------------------

    total_value = sum(
        (
            reservation.total_amount
            for reservation in reservations
        ),
        Decimal("0.00"),
    )

    # -------------------------------------------------
    # RENDER
    # -------------------------------------------------

    return render(
        request,
        "customers/customer_detail.html",
        {
            "business": business,
            "customer": customer,
            "reservations": reservations,

            "total_reservations": total_reservations,
            "active_reservations": active_reservations,
            "completed_reservations": completed_reservations,
            "cancelled_reservations": cancelled_reservations,
            "total_value": total_value,
        },
    )