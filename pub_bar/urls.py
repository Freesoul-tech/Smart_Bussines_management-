from django.urls import path

from . import views


app_name = "pub_bar"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("products/", views.section, {"name": "products"}, name="products"),
    path("products/add/", views.section, {"name": "products", "create": True}, name="products_add"),
    path("products/<int:object_id>/edit/", views.section, {"name": "products"}, name="products_edit"),
    path("categories/", views.section, {"name": "categories"}, name="categories"),
    path("categories/add/", views.section, {"name": "categories", "create": True}, name="categories_add"),
    path("tables/", views.section, {"name": "tables"}, name="tables"),
    path("tables/add/", views.section, {"name": "tables", "create": True}, name="tables_add"),
    path("suppliers/", views.section, {"name": "suppliers"}, name="suppliers"),
    path("suppliers/add/", views.section, {"name": "suppliers", "create": True}, name="suppliers_add"),
    path("inventory/", views.section, {"name": "inventory"}, name="inventory"),
    path("inventory/add/", views.section, {"name": "inventory", "create": True}, name="inventory_add"),
    path("orders/", views.section, {"name": "orders"}, name="orders"),
    path("orders/add/", views.order_add, name="orders_add"),
    path("reservations/", views.section, {"name": "reservations"}, name="reservations"),
    path("reservations/add/", views.section, {"name": "reservations", "create": True}, name="reservations_add"),
    path("payments/", views.payments, name="payments"),
    path("payments/add/", views.payment_add, name="payment_add"),
    path("reports/", views.reports, name="reports"),
]
