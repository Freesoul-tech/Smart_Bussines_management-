from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from businesses.models import (
    BoutiqueCategory,
    BoutiqueInventoryMovement,
    BoutiqueOrder,
    BoutiqueOrderItem,
    BoutiqueProduct,
    BoutiqueProfile,
)
from core.access import get_user_business
from payments.models import Payment

from .forms import (
    BoutiqueCategoryForm,
    BoutiqueInventoryForm,
    BoutiqueOrderForm,
    BoutiquePaymentForm,
    BoutiqueProductForm,
    BoutiqueProfileForm,
)

SECTIONS = {
    "products": ("Products", BoutiqueProduct, BoutiqueProductForm),
    "categories": ("Categories", BoutiqueCategory, BoutiqueCategoryForm),
    "inventory": ("Inventory", BoutiqueInventoryMovement, BoutiqueInventoryForm),
}


def get_boutique(request):
    business = get_user_business(request.user)
    if not business:
        return None
    if business.business_model != "boutique":
        return redirect("dashboard:dashboard")
    return business


@login_required
def dashboard(request):
    business = get_boutique(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    products = BoutiqueProduct.objects.filter(business=business)
    orders = BoutiqueOrder.objects.filter(business=business)
    return render(request, "boutique/dashboard.html", {
        "business": business,
        "product_count": products.count(),
        "category_count": BoutiqueCategory.objects.filter(business=business).count(),
        "sale_count": orders.count(),
        "stock_value": sum(
            (product.stock_quantity * product.selling_price for product in products),
            Decimal("0.00"),
        ),
        "low_stock_count": sum(product.is_low_stock for product in products),
    })


@login_required
def profile(request):
    business = get_boutique(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    instance, _ = BoutiqueProfile.objects.get_or_create(business=business)
    form = BoutiqueProfileForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("boutique:profile")
    return render(request, "boutique/form.html", {
        "business": business, "form": form, "title": "Boutique Profile", "back_url": "boutique:dashboard",
    })


@login_required
def section(request, name, object_id=None, create=False):
    business = get_boutique(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    title, model, form_class = SECTIONS[name]
    queryset = (
        model.objects.filter(product__business=business)
        if name == "inventory" else model.objects.filter(business=business)
    )
    instance = get_object_or_404(queryset, id=object_id) if object_id else None
    form = form_class(request.POST or None, instance=instance, business=business)
    if create and request.method == "GET":
        return render(request, "boutique/form.html", {
            "business": business, "form": form, "title": f"Add {title[:-1] if title.endswith('s') else title}",
            "back_url": f"boutique:{name}",
        })
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        if hasattr(item, "business_id"):
            item.business = business
        item.save()
        if name == "inventory":
            try:
                apply_inventory_movement(item)
            except ValidationError as error:
                item.delete()
                form.add_error(None, error.message)
                return render(request, "boutique/form.html", {
                    "business": business, "form": form, "title": title, "back_url": f"boutique:{name}",
                })
        return redirect(f"boutique:{name}")
    related_fields = {"products": ("category",), "inventory": ("product",)}
    records = queryset.select_related(*related_fields.get(name, ()))
    return render(request, "boutique/section.html", {
        "business": business, "title": title, "name": name, "form": form,
        "records": records, "add_url": f"boutique:{name}_add",
    })


@transaction.atomic
def apply_inventory_movement(movement):
    product = BoutiqueProduct.objects.select_for_update().get(id=movement.product_id)
    quantity = movement.quantity if movement.movement_type != "stock_out" else -movement.quantity
    if product.stock_quantity + quantity < 0:
        raise ValidationError(f"Insufficient stock for {product.name}.")
    product.stock_quantity += quantity
    product.save(update_fields=["stock_quantity", "updated_at"])


@login_required
def sales(request):
    business = get_boutique(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    form = BoutiqueOrderForm(request.POST or None, business=business)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            order = form.save(commit=False)
            order.business = business
            order.save()
            product = form.cleaned_data["product"]
            quantity = form.cleaned_data["quantity"]
            locked_product = BoutiqueProduct.objects.select_for_update().get(id=product.id)
            if locked_product.stock_quantity < quantity:
                form.add_error("quantity", f"Only {locked_product.stock_quantity} units are in stock.")
                transaction.set_rollback(True)
            else:
                BoutiqueOrderItem.objects.create(
                    order=order, product=locked_product, quantity=quantity,
                    unit_price=locked_product.selling_price,
                )
                locked_product.stock_quantity -= quantity
                locked_product.save(update_fields=["stock_quantity", "updated_at"])
        if not form.errors:
            return redirect("boutique:sales")
    records = BoutiqueOrder.objects.filter(business=business).select_related("customer")
    return render(request, "boutique/sales.html", {
        "business": business, "form": form, "records": records,
    })


@login_required
def payments(request):
    business = get_boutique(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    form = BoutiquePaymentForm(request.POST or None, business=business)
    if request.method == "POST" and form.is_valid():
        payment = form.save(commit=False)
        payment.business = business
        payment.save()
        return redirect("boutique:payments")
    rows = Payment.objects.filter(business=business, boutique_order__isnull=False).select_related("boutique_order")
    return render(request, "boutique/payments.html", {
        "business": business, "form": form, "payments": rows,
        "total_paid": rows.filter(status="paid").aggregate(total=Sum("amount"))["total"] or Decimal("0.00"),
    })


@login_required
def reports(request):
    business = get_boutique(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business
    orders = BoutiqueOrder.objects.filter(business=business).exclude(status="cancelled")
    paid = Payment.objects.filter(
        business=business, boutique_order__isnull=False, status="paid",
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    return render(request, "boutique/reports.html", {
        "business": business,
        "sales_total": sum((order.total_amount for order in orders), Decimal("0.00")),
        "paid_total": paid,
        "sale_count": orders.count(),
        "product_count": BoutiqueProduct.objects.filter(business=business).count(),
    })
