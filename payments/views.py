from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from businesses.models import Business
from core.access import business_permission_required, get_user_business
from reservations.models import Reservation

from .forms import PaymentForm
from .models import Payment


@login_required
@business_permission_required("payments.view_payment")
def payment_list(request):

    # -------------------------------------------------
    # GET USER'S BUSINESS
    # -------------------------------------------------

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    # -------------------------------------------------
    # GET PAYMENTS
    # -------------------------------------------------

    payments = (
        Payment.objects.filter(
            business=business
        )
        .select_related(
            "reservation",
            "reservation__room",
        )
    )

    # -------------------------------------------------
    # PAYMENT SUMMARY
    # -------------------------------------------------

    total_paid = (
        Payment.objects.filter(
            business=business,
            status="paid",
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    total_refunded = (
        Payment.objects.filter(
            business=business,
            status="refunded",
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    # -------------------------------------------------
    # RESERVATION FINANCIAL INFORMATION
    # -------------------------------------------------

    reservation_data = {}

    reservations = (
        Reservation.objects.filter(
            business=business
        )
        .select_related("room")
    )

    total_revenue = Decimal("0.00")
    total_balance = Decimal("0.00")

    for reservation in reservations:

        # Number of nights
        nights = (
            reservation.check_out
            - reservation.check_in
        ).days

        if nights < 1:
            nights = 1

        # Reservation total
        reservation_total = (
            Decimal(nights)
            * reservation.room.price_per_night
        )

        # Total paid for reservation
        amount_paid = (
            Payment.objects.filter(
                reservation=reservation,
                status="paid",
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        # Remaining balance
        balance = (
            reservation_total
            - amount_paid
        )

        if balance < 0:
            balance = Decimal("0.00")

        reservation_data[reservation.id] = {
            "nights": nights,
            "reservation_total": reservation_total,
            "amount_paid": amount_paid,
            "balance": balance,
        }

        # Do not count cancelled reservations
        if reservation.status != "cancelled":

            total_revenue += reservation_total
            total_balance += balance

    # -------------------------------------------------
    # ADD FINANCIAL DATA TO PAYMENTS
    # -------------------------------------------------

    payment_rows = []

    for payment in payments:

        data = reservation_data.get(
            payment.reservation_id
        )

        if data:

            payment.reservation_total = (
                data["reservation_total"]
            )

            payment.total_paid = (
                data["amount_paid"]
            )

            payment.balance = (
                data["balance"]
            )

            payment.nights = (
                data["nights"]
            )

        else:

            payment.reservation_total = Decimal(
                "0.00"
            )

            payment.total_paid = Decimal(
                "0.00"
            )

            payment.balance = Decimal(
                "0.00"
            )

            payment.nights = 0

        payment_rows.append(payment)

    # -------------------------------------------------
    # PAYMENT COUNT
    # -------------------------------------------------

    payment_count = payments.count()

    # -------------------------------------------------
    # RENDER PAYMENT LIST
    # -------------------------------------------------

    return render(
        request,
        "payments/payment_list.html",
        {
            "business": business,
            "payments": payment_rows,
            "payment_count": payment_count,
            "total_revenue": total_revenue,
            "total_paid": total_paid,
            "total_refunded": total_refunded,
            "total_balance": total_balance,
        },
    )


@login_required
@business_permission_required("payments.add_payment")
def payment_add(request):

    # -------------------------------------------------
    # GET USER'S BUSINESS
    # -------------------------------------------------

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    # -------------------------------------------------
    # HANDLE FORM SUBMISSION
    # -------------------------------------------------

    if request.method == "POST":

        form = PaymentForm(
            request.POST,
            business=business,
        )

        if form.is_valid():

            payment = form.save(
                commit=False
            )

            payment.business = business

            payment.save()

            return redirect(
                "payment_list"
            )

    else:

        form = PaymentForm(
            business=business,
        )

    # -------------------------------------------------
    # RENDER PAYMENT FORM
    # -------------------------------------------------

    return render(
        request,
        "payments/payment_form.html",
        {
            "form": form,
            "business": business,
        },
    )


@login_required
@business_permission_required("payments.change_payment")
def payment_edit(
    request,
    payment_id,
):

    # -------------------------------------------------
    # GET USER'S BUSINESS
    # -------------------------------------------------

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    # -------------------------------------------------
    # GET PAYMENT
    # -------------------------------------------------

    payment = get_object_or_404(
        Payment.objects.select_related(
            "business",
            "reservation",
        ),
        id=payment_id,
        business=business,
    )

    # -------------------------------------------------
    # HANDLE FORM SUBMISSION
    # -------------------------------------------------

    if request.method == "POST":

        form = PaymentForm(
            request.POST,
            instance=payment,
            business=business,
        )

        if form.is_valid():

            payment = form.save(
                commit=False
            )

            payment.business = business

            payment.save()

            return redirect(
                "payment_list"
            )

    else:

        form = PaymentForm(
            instance=payment,
            business=business,
        )

    # -------------------------------------------------
    # RENDER EDIT FORM
    # -------------------------------------------------

    return render(
        request,
        "payments/payment_form.html",
        {
            "form": form,
            "business": business,
            "editing": True,
            "payment": payment,
        },
    )

