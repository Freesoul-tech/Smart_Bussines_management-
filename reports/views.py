from datetime import timedelta
from decimal import Decimal
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from customers.models import Customer
from payments.models import Payment
from reservations.models import Reservation
from businesses.models import Order
from core.access import business_permission_required, get_user_business

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def get_report_data(business, period):
    """
    Build the report data using exactly the same filtering
    rules as the report dashboard.
    """

    today = timezone.localdate()

    reservations = Reservation.objects.filter(
        business=business
    )

    payments = Payment.objects.filter(
        business=business
    )

    customers = Customer.objects.filter(
        business=business
    )

    restaurant_orders = Order.objects.none()
    if business.business_model == "restaurant":
        restaurant_orders = Order.objects.filter(
            restaurant__business=business
        ).exclude(status="cancelled")

    # =========================================================
    # DATE FILTER
    # =========================================================

    if period == "today":

        reservations = reservations.filter(
            check_in=today
        )

        payments = payments.filter(
            created_at__date=today
        )

        customers = customers.filter(
            created_at__date=today
        )
        restaurant_orders = restaurant_orders.filter(created_at__date=today)

    elif period == "week":

        start_of_week = (
            today
            - timedelta(days=today.weekday())
        )

        reservations = reservations.filter(
            check_in__gte=start_of_week,
            check_in__lte=today,
        )

        payments = payments.filter(
            created_at__date__gte=start_of_week,
            created_at__date__lte=today,
        )

        customers = customers.filter(
            created_at__date__gte=start_of_week,
            created_at__date__lte=today,
        )
        restaurant_orders = restaurant_orders.filter(
            created_at__date__gte=start_of_week,
            created_at__date__lte=today,
        )

    elif period == "month":

        start_of_month = today.replace(
            day=1
        )

        reservations = reservations.filter(
            check_in__gte=start_of_month,
            check_in__lte=today,
        )

        payments = payments.filter(
            created_at__date__gte=start_of_month,
            created_at__date__lte=today,
        )

        customers = customers.filter(
            created_at__date__gte=start_of_month,
            created_at__date__lte=today,
        )
        restaurant_orders = restaurant_orders.filter(
            created_at__date__gte=start_of_month,
            created_at__date__lte=today,
        )

    elif period == "year":

        start_of_year = today.replace(
            month=1,
            day=1,
        )

        reservations = reservations.filter(
            check_in__gte=start_of_year,
            check_in__lte=today,
        )

        payments = payments.filter(
            created_at__date__gte=start_of_year,
            created_at__date__lte=today,
        )

        customers = customers.filter(
            created_at__date__gte=start_of_year,
            created_at__date__lte=today,
        )
        restaurant_orders = restaurant_orders.filter(
            created_at__date__gte=start_of_year,
            created_at__date__lte=today,
        )

    # =========================================================
    # FINANCIAL SUMMARY
    # =========================================================

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

    # =========================================================
    # RESERVATION REVENUE
    # =========================================================

    total_revenue = Decimal("0.00")

    for reservation in reservations:

        if reservation.status == "cancelled":
            continue

        total_revenue += reservation.total_amount

    for order in restaurant_orders.prefetch_related("items"):
        total_revenue += order.total_amount

    # =========================================================
    # OUTSTANDING
    # =========================================================

    outstanding_balance = (
        total_revenue
        - total_paid
    )

    if outstanding_balance < Decimal("0.00"):
        outstanding_balance = Decimal("0.00")

    # =========================================================
    # RESERVATION STATUS
    # =========================================================

    total_reservations = reservations.count()

    pending_reservations = reservations.filter(
        status="pending"
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

    cancelled_reservations = reservations.filter(
        status="cancelled"
    ).count()

    # =========================================================
    # CUSTOMERS
    # =========================================================

    total_customers = customers.count()

    # =========================================================
    # PAYMENTS
    # =========================================================

    total_payments = payments.count()

    # =========================================================
    # PAYMENT METHODS
    # =========================================================

    cash_payments = (
        payments.filter(
            status="paid",
            payment_method="cash",
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    card_payments = (
        payments.filter(
            status="paid",
            payment_method="card",
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    mobile_money_payments = (
        payments.filter(
            status="paid",
            payment_method="mobile_money",
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    bank_transfer_payments = (
        payments.filter(
            status="paid",
            payment_method="bank_transfer",
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    return {
        "today": today,
        "total_revenue": total_revenue,
        "total_paid": total_paid,
        "outstanding_balance": outstanding_balance,
        "total_refunded": total_refunded,
        "total_reservations": total_reservations,
        "pending_reservations": pending_reservations,
        "confirmed_reservations": confirmed_reservations,
        "checked_in_reservations": checked_in_reservations,
        "checked_out_reservations": checked_out_reservations,
        "cancelled_reservations": cancelled_reservations,
        "total_customers": total_customers,
        "total_payments": total_payments,
        "cash_payments": cash_payments,
        "card_payments": card_payments,
        "mobile_money_payments": mobile_money_payments,
        "bank_transfer_payments": bank_transfer_payments,
    }


@login_required
@business_permission_required("settings_app.view_reports")
def report_dashboard(request):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    period = request.GET.get(
        "period",
        "all",
    )

    data = get_report_data(
        business,
        period,
    )

    context = {
        "business": business,
        "date_filter": period,

        "total_revenue": data["total_revenue"],
        "total_paid": data["total_paid"],
        "outstanding_balance": data["outstanding_balance"],
        "total_refunded": data["total_refunded"],

        "total_reservations": data["total_reservations"],
        "pending_reservations": data["pending_reservations"],
        "confirmed_reservations": data["confirmed_reservations"],
        "checked_in_reservations": data["checked_in_reservations"],
        "checked_out_reservations": data["checked_out_reservations"],
        "cancelled_reservations": data["cancelled_reservations"],

        "total_customers": data["total_customers"],
        "total_payments": data["total_payments"],

        "cash_payments": data["cash_payments"],
        "card_payments": data["card_payments"],
        "mobile_money_payments": data["mobile_money_payments"],
        "bank_transfer_payments": data["bank_transfer_payments"],
    }

    return render(
        request,
        "reports/report_dashboard.html",
        context,
    )


@login_required
@business_permission_required("settings_app.view_reports")
def report_pdf_preview(request):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    period = request.GET.get(
        "period",
        "all",
    )

    data = get_report_data(
        business,
        period,
    )

    period_names = {
        "all": "All Time",
        "today": "Today",
        "week": "This Week",
        "month": "This Month",
        "year": "This Year",
    }

    period_label = period_names.get(
        period,
        "All Time",
    )

    context = {
        "business": business,
        "period": period,
        "period_label": period_label,
        "data": data,
    }

    return render(
        request,
        "reports/report_pdf_preview.html",
        context,
    )
@login_required
@business_permission_required("settings_app.view_reports")
def export_report_pdf(request):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    period = request.GET.get(
        "period",
        "all",
    )

    data = get_report_data(
        business,
        period,
    )

    period_names = {
        "all": "All Time",
        "today": "Today",
        "week": "This Week",
        "month": "This Month",
        "year": "This Year",
    }

    period_label = period_names.get(
        period,
        "All Time",
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="SBMS Business Report",
        author="Smart Business Management Suite",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=16,
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
    )

    story = []

    # =========================================================
    # HEADER
    # =========================================================

    story.append(
        Paragraph(
            "Smart Business Management Suite",
            title_style,
        )
    )

    story.append(
        Paragraph(
            f"{business.name} — Business Report",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            f"Report Period: <b>{period_label}</b>",
            normal_style,
        )
    )

    story.append(
        Paragraph(
            f"Generated: {data['today'].strftime('%d %B %Y')}",
            normal_style,
        )
    )

    story.append(Spacer(1, 10))

    # =========================================================
    # FINANCIAL SUMMARY
    # =========================================================

    story.append(
        Paragraph(
            "Financial Summary",
            section_style,
        )
    )

    financial_data = [
        ["Metric", "Amount"],
        [
            "Total Revenue",
            f"MWK {data['total_revenue']:,.2f}",
        ],
        [
            "Total Paid",
            f"MWK {data['total_paid']:,.2f}",
        ],
        [
            "Outstanding Balance",
            f"MWK {data['outstanding_balance']:,.2f}",
        ],
        [
            "Total Refunded",
            f"MWK {data['total_refunded']:,.2f}",
        ],
    ]

    financial_table = Table(
        financial_data,
        colWidths=[
            95 * mm,
            65 * mm,
        ],
    )

    financial_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1f2937"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#d1d5db"),
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(financial_table)

    # =========================================================
    # BUSINESS ACTIVITY
    # =========================================================

    story.append(
        Paragraph(
            "Business Activity",
            section_style,
        )
    )

    activity_data = [
        ["Metric", "Count"],
        [
            "Total Reservations",
            str(data["total_reservations"]),
        ],
        [
            "Total Customers",
            str(data["total_customers"]),
        ],
        [
            "Total Payments",
            str(data["total_payments"]),
        ],
    ]

    activity_table = Table(
        activity_data,
        colWidths=[
            95 * mm,
            65 * mm,
        ],
    )

    activity_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1f2937"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#d1d5db"),
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(activity_table)

    # =========================================================
    # RESERVATION STATUS
    # =========================================================

    story.append(
        Paragraph(
            "Reservation Status",
            section_style,
        )
    )

    reservation_data = [
        ["Status", "Reservations"],
        [
            "Pending",
            str(data["pending_reservations"]),
        ],
        [
            "Confirmed",
            str(data["confirmed_reservations"]),
        ],
        [
            "Checked In",
            str(data["checked_in_reservations"]),
        ],
        [
            "Checked Out",
            str(data["checked_out_reservations"]),
        ],
        [
            "Cancelled",
            str(data["cancelled_reservations"]),
        ],
    ]

    reservation_table = Table(
        reservation_data,
        colWidths=[
            95 * mm,
            65 * mm,
        ],
    )

    reservation_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1f2937"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#d1d5db"),
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(reservation_table)

    # =========================================================
    # PAYMENT METHODS
    # =========================================================

    story.append(
        Paragraph(
            "Payment Methods",
            section_style,
        )
    )

    payment_data = [
        ["Payment Method", "Amount"],
        [
            "Cash",
            f"MWK {data['cash_payments']:,.2f}",
        ],
        [
            "Card",
            f"MWK {data['card_payments']:,.2f}",
        ],
        [
            "Mobile Money",
            f"MWK {data['mobile_money_payments']:,.2f}",
        ],
        [
            "Bank Transfer",
            f"MWK {data['bank_transfer_payments']:,.2f}",
        ],
    ]

    payment_table = Table(
        payment_data,
        colWidths=[
            95 * mm,
            65 * mm,
        ],
    )

    payment_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1f2937"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#d1d5db"),
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(payment_table)

    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "Generated by Smart Business Management Suite.",
            subtitle_style,
        )
    )

    document.build(story)

    buffer.seek(0)

    filename = (
        f"SBMS_Report_{period_label.replace(' ', '_')}.pdf"
    )

    return FileResponse(
        buffer,
        as_attachment=False,
        filename=filename,
        content_type="application/pdf",
    )