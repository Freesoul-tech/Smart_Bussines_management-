from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from businesses.models import (
    PubBarCategory,
    PubBarInventoryMovement,
    PubBarOrder,
    PubBarOrderItem,
    PubBarProduct,
    PubBarProfile,
    PubBarReservation,
    PubBarSupplier,
    PubBarTable,
)
from core.access import get_user_business
from payments.models import Payment

from .forms import (
    PubBarCategoryForm,
    PubBarInventoryForm,
    PubBarOrderForm,
    PubBarPaymentForm,
    PubBarProductForm,
    PubBarProfileForm,
    PubBarReservationForm,
    PubBarSupplierForm,
    PubBarTableForm,
)

SECTIONS = {
    "products": ("Drinks", PubBarProduct, PubBarProductForm),
    "categories": ("Categories", PubBarCategory, PubBarCategoryForm),
    "tables": ("Tables", PubBarTable, PubBarTableForm),
    "suppliers": ("Suppliers", PubBarSupplier, PubBarSupplierForm),
    "inventory": ("Inventory", PubBarInventoryMovement, PubBarInventoryForm),
    "reservations": ("Reservations", PubBarReservation, PubBarReservationForm),
    "orders": ("Orders", PubBarOrder, PubBarOrderForm),
}


def get_pub_bar(request):
    business = get_user_business(request.user)
    if not business:
        return None
    if business.business_model != "pub_bar":
        return redirect("dashboard:dashboard")
    return business


@login_required
def dashboard(request):
    business = get_pub_bar(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    products = PubBarProduct.objects.filter(business=business)
    orders = PubBarOrder.objects.filter(business=business)
    return render(request, "pub_bar/dashboard.html", {
        "business": business,
        "product_count": products.count(),
        "table_count": PubBarTable.objects.filter(business=business, is_active=True).count(),
        "order_count": orders.count(),
        "stock_value": sum((p.stock_quantity * p.selling_price for p in products), Decimal("0.00")),
    })


@login_required
def profile(request):
    business = get_pub_bar(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    instance, _ = PubBarProfile.objects.get_or_create(business=business)
    form = PubBarProfileForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("pub_bar:profile")
    return render(request, "pub_bar/form.html", {"business": business, "form": form, "title": "Business Profile", "back_url": "pub_bar:dashboard"})


@login_required
def section(request, name, object_id=None, create=False):
    business = get_pub_bar(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    title, model, form_class = SECTIONS[name]
    queryset = (
        model.objects.filter(product__business=business)
        if name == "inventory"
        else model.objects.filter(business=business)
    )
    instance = get_object_or_404(queryset, id=object_id) if object_id else None
    form = form_class(request.POST or None, instance=instance, business=business)
    if create and request.method == "GET":
        return render(request, "pub_bar/form.html", {"business": business, "form": form, "title": f"Add {title}", "back_url": f"pub_bar:{name}"})
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        if hasattr(item, "business_id"):
            item.business = business
        item.save()
        if name == "orders":
            product = form.cleaned_data["product"]
            PubBarOrderItem.objects.create(
                order=item,
                product=product,
                quantity=form.cleaned_data["quantity"],
                unit_price=product.selling_price,
            )
        if name == "inventory":
            try:
                apply_inventory_movement(item)
            except ValidationError as error:
                item.delete()
                form.add_error(None, error.message)
                return render(request, "pub_bar/form.html", {"business": business, "form": form, "title": title, "back_url": f"pub_bar:{name}"})
        return redirect(f"pub_bar:{name}")
    related_fields = {
        "products": ("category",),
        "inventory": ("product", "supplier"),
        "orders": ("table", "customer"),
        "reservations": ("table", "customer"),
    }
    records = queryset.select_related(*related_fields.get(name, ()))
    return render(request, "pub_bar/section.html", {"business": business, "title": title, "name": name, "form": form, "records": records, "add_url": f"pub_bar:{name}_add"})


@transaction.atomic
def apply_inventory_movement(movement):
    product = PubBarProduct.objects.select_for_update().get(id=movement.product_id)
    quantity = movement.quantity
    if movement.movement_type == "stock_out":
        quantity = -quantity
    elif movement.movement_type == "adjustment":
        quantity = movement.quantity
    if product.stock_quantity + quantity < 0:
        raise ValidationError(f"Insufficient stock for {product.name}.")
    product.stock_quantity += quantity
    product.save(update_fields=["stock_quantity", "updated_at"])


@login_required
def order_add(request):
    business = get_pub_bar(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    form = PubBarOrderForm(request.POST or None, business=business)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            order = form.save(commit=False)
            order.business = business
            order.save()
            product = form.cleaned_data["product"]
            PubBarOrderItem.objects.create(order=order, product=product, quantity=form.cleaned_data["quantity"], unit_price=product.selling_price)
        return redirect("pub_bar:orders")
    return render(request, "pub_bar/form.html", {"business": business, "form": form, "title": "New Order", "back_url": "pub_bar:orders"})


@login_required
def payments(request):
    business = get_pub_bar(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    rows = Payment.objects.filter(business=business, pub_bar_order__isnull=False).select_related("pub_bar_order", "pub_bar_order__customer")
    return render(request, "pub_bar/payments.html", {"business": business, "payments": rows, "total_paid": rows.filter(status="paid").aggregate(total=Sum("amount"))["total"] or Decimal("0.00")})


@login_required
def payment_add(request):
    business = get_pub_bar(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    form = PubBarPaymentForm(request.POST or None, business=business)
    if request.method == "POST" and form.is_valid():
        payment = form.save(commit=False)
        payment.business = business
        payment.save()
        return redirect("pub_bar:payments")
    return render(request, "pub_bar/form.html", {"business": business, "form": form, "title": "Record Payment", "back_url": "pub_bar:payments"})


@login_required
def reports(request):
    business = get_pub_bar(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    orders = PubBarOrder.objects.filter(business=business).exclude(status="cancelled")
    paid = Payment.objects.filter(business=business, pub_bar_order__isnull=False, status="paid").aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    return render(request, "pub_bar/reports.html", {"business": business, "orders": orders, "sales_total": sum((o.total_amount for o in orders), Decimal("0.00")), "paid_total": paid, "product_count": PubBarProduct.objects.filter(business=business).count()})
