from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from businesses.models import (
    BakeryCategory,
    BakeryExpense,
    BakeryIngredient,
    BakeryOrder,
    BakeryOrderItem,
    BakeryProduction,
    BakeryProduct,
    BakeryProfile,
    BakeryRecipe,
    BakeryRecipeIngredient,
    BakeryStockMovement,
    BakerySupplier,
)
from core.access import get_user_business
from customers.models import Customer
from payments.models import Payment

from .forms import (
    BakeryExpenseForm,
    BakeryIngredientForm,
    BakeryOrderForm,
    BakeryProfileForm,
    BakeryProductionForm,
    BakeryProductForm,
    BakeryRecipeForm,
    BakerySupplierForm,
)


SECTION_CONFIG = {
    "products": {
        "title": "Products",
        "description": "Manage products, prices, stock, and availability.",
        "columns": ["Name", "Category", "Selling price", "Stock", "Available"],
    },
    "ingredients": {
        "title": "Ingredients",
        "description": "Track ingredient quantities, units, minimum stock, and suppliers.",
        "columns": ["Name", "Quantity", "Unit", "Minimum stock", "Supplier"],
    },
    "recipes": {
        "title": "Recipes",
        "description": "Connect bakery products to their required ingredients.",
        "columns": ["Product", "Ingredients", "Instructions"],
    },
    "production": {
        "title": "Production",
        "description": "Review production batches and quantities produced.",
        "columns": ["Product", "Quantity", "Production date", "Staff", "Status"],
    },
    "orders": {
        "title": "Sales / Orders",
        "description": "Review bakery sales and order items.",
        "columns": ["Order", "Customer", "Status", "Total", "Created"],
    },
    "suppliers": {
        "title": "Suppliers",
        "description": "Manage ingredient suppliers and contact information.",
        "columns": ["Name", "Phone", "Email", "Address", "Active"],
    },
    "expenses": {
        "title": "Expenses",
        "description": "Track bakery operating expenses.",
        "columns": ["Category", "Description", "Amount", "Date", "Notes"],
    },
    "inventory": {
        "title": "Stock Movement History",
        "description": "Audit ingredient deductions and product stock additions.",
        "columns": ["Item", "Type", "Quantity", "Notes", "Created"],
    },
}

ADD_URLS = {
    "products": "bakery:product_add",
    "ingredients": "bakery:ingredient_add",
    "recipes": "bakery:recipe_add",
    "production": "bakery:production_add",
    "orders": "bakery:order_add",
    "suppliers": "bakery:supplier_add",
    "expenses": "bakery:expense_add",
}

EDIT_URLS = {
    "products": "bakery:product_edit",
    "ingredients": "bakery:ingredient_edit",
    "recipes": "bakery:recipe_edit",
    "production": "bakery:production_edit",
    "suppliers": "bakery:supplier_edit",
    "expenses": "bakery:expense_edit",
}

FORM_CONFIG = {
    "products": (BakeryProduct, BakeryProductForm, "Product"),
    "ingredients": (BakeryIngredient, BakeryIngredientForm, "Ingredient"),
    "recipes": (BakeryRecipe, BakeryRecipeForm, "Recipe"),
    "production": (BakeryProduction, BakeryProductionForm, "Production batch"),
    "suppliers": (BakerySupplier, BakerySupplierForm, "Supplier"),
    "expenses": (BakeryExpense, BakeryExpenseForm, "Expense"),
}


def get_bakery(request):
    business = get_user_business(request.user)
    if not business:
        return None
    if business.business_model != "bakery":
        return redirect("dashboard:dashboard")
    return business


@transaction.atomic
def complete_production(production):
    product = BakeryProduct.objects.select_for_update().get(id=production.product_id)
    recipe = BakeryRecipe.objects.filter(product=product).first()
    if not recipe:
        raise ValidationError("Create a recipe before completing this production batch.")

    recipe_items = list(
        BakeryRecipeIngredient.objects
        .filter(recipe=recipe)
        .select_related("ingredient")
    )
    if not recipe_items:
        raise ValidationError("Add ingredients to the recipe before completing this production batch.")

    ingredient_ids = [item.ingredient_id for item in recipe_items]
    locked_ingredients = {
        ingredient.id: ingredient
        for ingredient in BakeryIngredient.objects.select_for_update().filter(id__in=ingredient_ids)
    }
    required_by_ingredient = {}
    for recipe_item in recipe_items:
        required_by_ingredient[recipe_item.ingredient_id] = (
            recipe_item.required_quantity * production.quantity_produced
        )

    for ingredient_id, required_quantity in required_by_ingredient.items():
        ingredient = locked_ingredients[ingredient_id]
        if ingredient.quantity_in_stock < required_quantity:
            raise ValidationError(
                f"Insufficient stock for {ingredient.name}. "
                f"Required {required_quantity} {ingredient.get_unit_display()}, "
                f"available {ingredient.quantity_in_stock}."
            )

    movement_note = f"Production batch #{production.id}"
    for ingredient_id, required_quantity in required_by_ingredient.items():
        ingredient = locked_ingredients[ingredient_id]
        ingredient.quantity_in_stock -= required_quantity
        ingredient.save(update_fields=["quantity_in_stock"])
        BakeryStockMovement.objects.create(
            ingredient=ingredient,
            movement_type="production",
            quantity=-required_quantity,
            notes=movement_note,
        )

    product.stock_quantity += production.quantity_produced
    product.save(update_fields=["stock_quantity", "updated_at"])
    BakeryStockMovement.objects.create(
        product=product,
        movement_type="production",
        quantity=production.quantity_produced,
        notes=movement_note,
    )


def bakery_form(request, section, object_id=None):
    business = get_bakery(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business

    model, form_class, title = FORM_CONFIG[section]
    instance = None
    if object_id:
        queryset = model.objects.all()
        if section == "recipes":
            queryset = queryset.filter(product__business=business)
        else:
            queryset = queryset.filter(business=business)
        instance = get_object_or_404(queryset, id=object_id)

    form = form_class(request.POST or None, instance=instance, business=business)
    if instance and section == "production" and instance.status == "completed":
        form.add_error(None, "Completed production batches cannot be edited because inventory has already been updated.")
        if request.method == "POST":
            return render(request, "bakery/form.html", {
                "business": business,
                "form": form,
                "page_title": f"Edit {title}",
                "section": section,
            })
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                item = form.save(commit=False)
                if hasattr(item, "business_id"):
                    item.business = business
                item.save()
                if section == "production" and item.status == "completed":
                    complete_production(item)
                if section == "recipes":
                    BakeryRecipeIngredient.objects.update_or_create(
                        recipe=item,
                        ingredient=form.cleaned_data["ingredient"],
                        defaults={"required_quantity": form.cleaned_data["required_quantity"]},
                    )
        except ValidationError as error:
            form.add_error(None, error.message)
            return render(request, "bakery/form.html", {
                "business": business,
                "form": form,
                "page_title": f"{'Edit' if instance else 'Add'} {title}",
                "section": section,
            })
        return redirect(f"bakery:{section}")

    return render(request, "bakery/form.html", {
        "business": business,
        "form": form,
        "page_title": f"{'Edit' if instance else 'Add'} {title}",
        "section": section,
    })


@login_required
def product_form(request, object_id=None):
    return bakery_form(request, "products", object_id)


@login_required
def ingredient_form(request, object_id=None):
    return bakery_form(request, "ingredients", object_id)


@login_required
def recipe_form(request, object_id=None):
    return bakery_form(request, "recipes", object_id)


@login_required
def production_form(request, object_id=None):
    return bakery_form(request, "production", object_id)


@login_required
def supplier_form(request, object_id=None):
    return bakery_form(request, "suppliers", object_id)


@login_required
def expense_form(request, object_id=None):
    return bakery_form(request, "expenses", object_id)


@login_required
def order_form(request):
    business = get_bakery(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business

    form = BakeryOrderForm(request.POST or None, business=business)
    if request.method == "POST" and form.is_valid():
        order = form.save(commit=False)
        order.business = business
        order.save()
        product = form.cleaned_data["product"]
        BakeryOrderItem.objects.create(
            order=order,
            product=product,
            quantity=form.cleaned_data["quantity"],
            unit_price=product.selling_price,
        )
        return redirect("bakery:orders")

    return render(request, "bakery/form.html", {
        "business": business,
        "form": form,
        "page_title": "Add Sales Order",
        "section": "orders",
    })


@login_required
def dashboard(request):
    business = get_bakery(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business

    products = BakeryProduct.objects.filter(business=business)
    ingredients = BakeryIngredient.objects.filter(business=business)
    orders = BakeryOrder.objects.filter(business=business)
    expenses = BakeryExpense.objects.filter(business=business)

    return render(request, "bakery/dashboard.html", {
        "business": business,
        "product_count": products.count(),
        "low_stock_count": ingredients.filter(
            quantity_in_stock__lte=F("minimum_stock"),
        ).count(),
        "order_count": orders.count(),
        "expense_total": expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00"),
    })


@login_required
def profile(request):
    business = get_bakery(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business

    instance, _ = BakeryProfile.objects.get_or_create(business=business)
    form = BakeryProfileForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("bakery:profile")

    return render(request, "bakery/profile.html", {
        "business": business,
        "form": form,
    })


@login_required
def section_list(request, section):
    business = get_bakery(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business

    config = SECTION_CONFIG[section]
    records = []

    if section == "products":
        records = [{"id": p.id, "values": [p.name, p.category or "-", p.selling_price, p.stock_quantity, "Yes" if p.is_available else "No"]} for p in BakeryProduct.objects.filter(business=business)]
    elif section == "ingredients":
        records = [{"id": i.id, "values": [i.name, i.quantity_in_stock, i.get_unit_display(), i.minimum_stock, i.supplier or "-"]} for i in BakeryIngredient.objects.filter(business=business)]
    elif section == "recipes":
        recipes = BakeryRecipe.objects.filter(product__business=business).prefetch_related("ingredients__ingredient")
        records = [{"id": r.id, "values": [r.product.name, ", ".join(item.ingredient.name for item in r.ingredients.all()) or "-", r.instructions or "-"]} for r in recipes]
    elif section == "production":
        batches = BakeryProduction.objects.filter(business=business).select_related("product", "staff")
        records = [{"id": b.id, "values": [b.product.name, b.quantity_produced, b.production_date, b.staff or "-", b.get_status_display()]} for b in batches]
    elif section == "orders":
        orders = BakeryOrder.objects.filter(business=business).select_related("customer")
        records = [{"id": o.id, "values": [f"Order #{o.id}", o.customer or "Walk-in", o.get_status_display(), o.total_amount, o.created_at]} for o in orders]
    elif section == "suppliers":
        records = [{"id": s.id, "values": [s.name, s.phone or "-", s.email or "-", s.address or "-", "Yes" if s.is_active else "No"]} for s in BakerySupplier.objects.filter(business=business)]
    elif section == "expenses":
        records = [{"id": e.id, "values": [e.category, e.description, e.amount, e.expense_date, e.notes or "-"]} for e in BakeryExpense.objects.filter(business=business)]
    elif section == "inventory":
        movements = BakeryStockMovement.objects.filter(
            Q(product__business=business) | Q(ingredient__business=business),
        ).select_related("product", "ingredient")
        records = [{"values": [m.product or m.ingredient, m.get_movement_type_display(), m.quantity, m.notes or "-", m.created_at]} for m in movements]

    return render(request, "bakery/section_list.html", {
        "business": business,
        "section": section,
        "section_title": config["title"],
        "description": config["description"],
        "columns": config["columns"],
        "records": records,
        "add_url": ADD_URLS.get(section),
        "edit_url": EDIT_URLS.get(section),
    })


@login_required
def reports(request):
    business = get_bakery(request)
    if business is None:
        return redirect("businesses:business_setup")
    if not hasattr(business, "business_model"):
        return business

    orders = BakeryOrder.objects.filter(business=business).exclude(status="cancelled")
    payments = Payment.objects.filter(business=business, bakery_order__isnull=False)
    expenses = BakeryExpense.objects.filter(business=business)

    sales_total = sum((order.total_amount for order in orders), Decimal("0.00"))
    paid_total = payments.filter(status="paid").aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    expense_total = expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    return render(request, "bakery/reports.html", {
        "business": business,
        "sales_total": sales_total,
        "paid_total": paid_total,
        "expense_total": expense_total,
        "revenue_total": paid_total - expense_total,
        "production_count": BakeryProduction.objects.filter(business=business).count(),
        "ingredient_count": BakeryIngredient.objects.filter(business=business).count(),
        "customer_count": Customer.objects.filter(business=business).count(),
    })
