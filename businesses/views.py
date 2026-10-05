from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from payments.models import Payment

from employees.models import Employee

from .forms import (
    BusinessSetupForm,
    MenuCategoryForm,
    MenuItemForm,
    OrderStatusForm,
    RestaurantReservationForm,
    RestaurantOrderForm,
    RestaurantPaymentForm,
    RestaurantTableForm,
)
from .models import (
    Customer,
    MenuCategory,
    MenuItem,
    Order,
    OrderItem,
    Reservation,
    Restaurant,
    RestaurantTable,
)


@login_required
def business_setup(request):
    existing_business = getattr(request.user, "business", None)

    if existing_business:
        return redirect("dashboard:dashboard")

    # -------------------------------------------------
    # BUSINESS SETUP
    # -------------------------------------------------
    if request.method == "POST":

        form = BusinessSetupForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            existing_business =getattr(request.user, "business", None)

            if existing_business:
                return redirect("dashboard:dashboard")

            business = form.save(
                commit=False
            )

            business.owner = request.user

            business.save()

            # -------------------------------------------------
            # OWNER AS EMPLOYEE
            # -------------------------------------------------
            Employee.objects.get_or_create(
                business=business,
                user=request.user,
                defaults={
                    "first_name": business.user_name,
                    "last_name": "",
                    "position": business.position,
                    "email": request.user.email,
                    "employment_status": "active",
                },
            )

            return redirect("dashboard:dashboard")

    else:

        form = BusinessSetupForm()

    # -------------------------------------------------
    # RENDER
    # -------------------------------------------------
    return render(
        request,
        "businesses/business_setup.html",
        {
            "form": form,
        },
    )



@login_required
def restaurant_dashboard(request):

    # =================================================
    # USER BUSINESS
    # =================================================

    business = getattr(request.user, "business", None)

    if not business:
        return redirect("business_setup")

    # =================================================
    # BUSINESS MODEL PROTECTION
    # =================================================

    if business.business_model != "restaurant":
        return redirect("dashboard:dashboard")

    # =================================================
    # RESTAURANT
    # =================================================

    restaurant, created = Restaurant.objects.get_or_create(
        business=business
    )

    # =================================================
    # MENU
    # =================================================

    menu_categories = (
        MenuCategory.objects
        .filter(
            restaurant=restaurant,
            is_active=True,
        )
        .prefetch_related("items")
        .order_by("name")
    )

    menu_items = (
        MenuItem.objects
        .filter(
            category__restaurant=restaurant,
            is_available=True,
        )
        .select_related("category")
        .order_by("name")
    )

    # =================================================
    # TABLES
    # =================================================

    tables = RestaurantTable.objects.filter(
        restaurant=restaurant,
        is_active=True,
    )

    total_tables = tables.count()

    available_tables = tables.filter(
        status="available"
    ).count()

    occupied_tables = tables.filter(
        status="occupied"
    ).count()

    reserved_tables = tables.filter(
        status="reserved"
    ).count()

    maintenance_tables = tables.filter(
        status="maintenance"
    ).count()

    # =================================================
    # CUSTOMERS
    # =================================================

    customers = Customer.objects.filter(
        restaurant=restaurant
    )

    total_customers = customers.count()

    # =================================================
    # ORDERS
    # =================================================

    orders = (
        Order.objects
        .filter(restaurant=restaurant)
        .select_related(
            "customer",
            "table",
        )
        .prefetch_related("items__menu_item")
        .order_by("-created_at")
    )

    total_orders = orders.count()

    pending_orders = orders.filter(
        status="pending"
    ).count()

    preparing_orders = orders.filter(
        status="preparing"
    ).count()

    ready_orders = orders.filter(
        status="ready"
    ).count()

    served_orders = orders.filter(
        status="served"
    ).count()

    completed_orders = orders.filter(
        status="completed"
    ).count()

    total_revenue = sum(
        (order.total_amount for order in orders if order.status != "cancelled"),
        0,
    )

    total_revenue = sum(
        (order.total_amount for order in orders if order.status != "cancelled"),
        0,
    )

    # =================================================
    # RESERVATIONS
    # =================================================

    reservations = (
        Reservation.objects
        .filter(restaurant=restaurant)
        .select_related(
            "customer",
            "table",
        )
        .order_by(
            "reservation_date",
            "reservation_time",
        )
    )

    total_reservations = reservations.count()

    pending_reservations = reservations.filter(
        status="pending"
    ).count()

    confirmed_reservations = reservations.filter(
        status="confirmed"
    ).count()

    seated_reservations = reservations.filter(
        status="seated"
    ).count()

    # =================================================
    # RECENT DATA
    # =================================================

    recent_orders = orders[:5]

    recent_reservations = reservations[:5]

    # =================================================
    # CONTEXT
    # =================================================

    context = {
        "business": business,
        "restaurant": restaurant,

        # Menu
        "menu_categories": menu_categories,
        "menu_items": menu_items,

        # Tables
        "tables": tables,
        "total_tables": total_tables,
        "available_tables": available_tables,
        "occupied_tables": occupied_tables,
        "reserved_tables": reserved_tables,
        "maintenance_tables": maintenance_tables,

        # Customers
        "customers": customers,
        "total_customers": total_customers,

        # Orders
        "orders": orders,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "preparing_orders": preparing_orders,
        "ready_orders": ready_orders,
        "served_orders": served_orders,
        "completed_orders": completed_orders,
        "total_revenue": total_revenue,
        "total_revenue": total_revenue,

        # Reservations
        "reservations": reservations,
        "total_reservations": total_reservations,
        "pending_reservations": pending_reservations,
        "confirmed_reservations": confirmed_reservations,
        "seated_reservations": seated_reservations,

        # Recent data
        "recent_orders": recent_orders,
        "recent_reservations": recent_reservations,
    }

    return render(
        request,
        "businesses/restaurant_dashboard.html",
        context,
    )


def _restaurant_for_user(request):
    business = getattr(request.user, "business", None)
    if not business or business.business_model != "restaurant":
        return None
    return Restaurant.objects.get_or_create(business=business)[0]


@login_required
def restaurant_products(request):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    if request.method == "POST":
        category_form = MenuCategoryForm(request.POST)
        if category_form.is_valid():
            category = category_form.save(commit=False)
            category.restaurant = restaurant
            category.save()
            messages.success(request, "Menu category added.")
            return redirect("businesses:restaurant_products")
    else:
        category_form = MenuCategoryForm()
    items = MenuItem.objects.filter(category__restaurant=restaurant).select_related("category")
    return render(request, "businesses/restaurant_products.html", {
        "business": restaurant.business,
        "restaurant": restaurant,
        "items": items,
        "category_form": category_form,
        "active_page": "products",
    })


@login_required
def restaurant_product_create(request):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    categories = MenuCategory.objects.filter(restaurant=restaurant)
    form = MenuItemForm(request.POST or None)
    form.fields["category"].queryset = categories
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product added to the menu.")
        return redirect("businesses:restaurant_products")
    return render(request, "businesses/restaurant_product_form.html", {
        "business": restaurant.business, "restaurant": restaurant, "form": form,
        "page_title": "Add product", "active_page": "products",
    })


@login_required
def restaurant_product_edit(request, item_id):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    item = get_object_or_404(MenuItem, pk=item_id, category__restaurant=restaurant)
    form = MenuItemForm(request.POST or None, instance=item)
    form.fields["category"].queryset = MenuCategory.objects.filter(restaurant=restaurant)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product updated.")
        return redirect("businesses:restaurant_products")
    return render(request, "businesses/restaurant_product_form.html", {
        "business": restaurant.business, "restaurant": restaurant, "form": form,
        "page_title": "Edit product", "active_page": "products",
    })


@login_required
def restaurant_product_delete(request, item_id):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    item = get_object_or_404(MenuItem, pk=item_id, category__restaurant=restaurant)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Product removed from the menu.")
    return redirect("businesses:restaurant_products")


@login_required
def restaurant_orders(request):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    orders = Order.objects.filter(restaurant=restaurant).select_related("customer", "table").prefetch_related("items__menu_item")
    return render(request, "businesses/restaurant_orders.html", {
        "business": restaurant.business, "restaurant": restaurant, "orders": orders,
        "active_page": "orders",
    })


@login_required
def restaurant_order_create(request):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    menu_items = MenuItem.objects.filter(
        category__restaurant=restaurant, is_available=True
    ).select_related("category")
    form = RestaurantOrderForm(request.POST or None, restaurant=restaurant)
    if request.method == "POST" and form.is_valid():
        quantities = request.POST.getlist("quantity")
        item_ids = request.POST.getlist("menu_item")
        selected_items = {
            str(item.id): item for item in menu_items.filter(id__in=item_ids)
        }
        lines = []
        for item_id, quantity in zip(item_ids, quantities):
            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                quantity = 0
            if quantity > 0 and item_id in selected_items:
                lines.append((selected_items[item_id], quantity))
        if not lines:
            form.add_error(None, "Select at least one product.")
        else:
            with transaction.atomic():
                order = form.save(commit=False)
                order.restaurant = restaurant
                order.save()
                OrderItem.objects.bulk_create([
                    OrderItem(order=order, menu_item=item, quantity=quantity, unit_price=item.price)
                    for item, quantity in lines
                ])
            messages.success(request, "Order saved with calculated total.")
            return redirect("businesses:restaurant_order_detail", order_id=order.id)
    return render(request, "businesses/restaurant_order_form.html", {
        "business": restaurant.business, "restaurant": restaurant, "form": form,
        "menu_items": menu_items, "active_page": "orders",
    })


@login_required
def restaurant_order_detail(request, order_id):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    order = get_object_or_404(
        Order.objects.select_related("customer", "table").prefetch_related("items__menu_item"),
        pk=order_id, restaurant=restaurant,
    )
    form = OrderStatusForm(request.POST or None, instance=order)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Order status updated.")
        return redirect("businesses:restaurant_order_detail", order_id=order.id)
    return render(request, "businesses/restaurant_order_detail.html", {
        "business": restaurant.business, "restaurant": restaurant, "order": order,
        "form": form, "active_page": "orders",
    })


@login_required
def restaurant_payments(request):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    payments = Payment.objects.filter(
        business=restaurant.business, restaurant_order__restaurant=restaurant
    ).select_related("restaurant_order", "restaurant_reservation").prefetch_related(
        "restaurant_order__items__menu_item", "restaurant_order__table"
    )
    orders = Order.objects.filter(restaurant=restaurant).exclude(status="cancelled").prefetch_related("items")
    total_revenue = sum((order.total_amount for order in orders), 0)
    total_paid = sum((payment.amount for payment in payments if payment.status == "paid"), 0)
    outstanding = max(total_revenue - total_paid, 0)
    return render(request, "businesses/restaurant_payments.html", {
        "business": restaurant.business, "restaurant": restaurant,
        "payments": payments, "total_revenue": total_revenue,
        "total_paid": total_paid, "outstanding": outstanding, "active_page": "payments",
    })


@login_required
def restaurant_payment_create(request):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    form = RestaurantPaymentForm(request.POST or None, restaurant=restaurant)
    if request.method == "POST" and form.is_valid():
        order = form.cleaned_data["order"]
        payment = Payment.objects.create(
            business=restaurant.business,
            restaurant_order=order,
            restaurant_reservation=form.cleaned_data["reservation"],
            amount=form.cleaned_data["amount"],
            payment_method=form.cleaned_data["payment_method"],
            status="paid",
            reference=form.cleaned_data["reference"],
            notes=form.cleaned_data["notes"],
        )
        messages.success(request, "Restaurant payment recorded.")
        return redirect("businesses:restaurant_payments")
    return render(request, "businesses/restaurant_payment_form.html", {
        "business": restaurant.business, "restaurant": restaurant,
        "form": form, "active_page": "payments",
    })


@login_required
def restaurant_tables(request):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    tables = RestaurantTable.objects.filter(restaurant=restaurant).prefetch_related(
        "orders__items__menu_item"
    )
    return render(request, "businesses/restaurant_tables.html", {
        "business": restaurant.business, "restaurant": restaurant, "tables": tables,
        "active_page": "tables",
    })


@login_required
def restaurant_table_form(request, table_id=None):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    table = get_object_or_404(RestaurantTable, pk=table_id, restaurant=restaurant) if table_id else None
    form = RestaurantTableForm(request.POST or None, instance=table)
    if request.method == "POST" and form.is_valid():
        saved_table = form.save(commit=False)
        saved_table.restaurant = restaurant
        saved_table.save()
        messages.success(request, "Table saved.")
        return redirect("businesses:restaurant_tables")
    return render(request, "businesses/restaurant_table_form.html", {
        "business": restaurant.business, "restaurant": restaurant, "form": form,
        "page_title": "Edit table" if table else "Add table", "active_page": "tables",
    })


@login_required
def restaurant_table_delete(request, table_id):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    table = get_object_or_404(RestaurantTable, pk=table_id, restaurant=restaurant)
    if request.method == "POST":
        table.delete()
        messages.success(request, "Table removed.")
    return redirect("businesses:restaurant_tables")


@login_required
def restaurant_reservations(request):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    reservations = Reservation.objects.filter(restaurant=restaurant).select_related("customer", "table")
    return render(request, "businesses/restaurant_reservations.html", {
        "business": restaurant.business, "restaurant": restaurant, "reservations": reservations,
        "active_page": "reservations",
    })


@login_required
def restaurant_reservation_form(request, reservation_id=None):
    restaurant = _restaurant_for_user(request)
    if not restaurant:
        return redirect("dashboard:dashboard")
    reservation = get_object_or_404(Reservation, pk=reservation_id, restaurant=restaurant) if reservation_id else None
    form = RestaurantReservationForm(request.POST or None, instance=reservation, restaurant=restaurant)
    if request.method == "POST" and form.is_valid():
        saved_reservation = form.save(commit=False)
        saved_reservation.restaurant = restaurant
        saved_reservation.save()
        messages.success(request, "Reservation saved.")
        return redirect("businesses:restaurant_reservations")
    return render(request, "businesses/restaurant_reservation_form.html", {
        "business": restaurant.business, "restaurant": restaurant, "form": form,
        "page_title": "Edit reservation" if reservation else "Add reservation", "active_page": "reservations",
    })
