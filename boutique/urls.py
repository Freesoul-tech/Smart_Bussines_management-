from django.urls import path

from . import views


app_name = "boutique"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("products/", views.section, {"name": "products"}, name="products"),
    path("products/add/", views.section, {"name": "products", "create": True}, name="products_add"),
    path("products/<int:object_id>/edit/", views.section, {"name": "products"}, name="products_edit"),
    path("categories/", views.section, {"name": "categories"}, name="categories"),
    path("categories/add/", views.section, {"name": "categories", "create": True}, name="categories_add"),
    path("inventory/", views.section, {"name": "inventory"}, name="inventory"),
    path("inventory/add/", views.section, {"name": "inventory", "create": True}, name="inventory_add"),
    path("sales/", views.sales, name="sales"),
    path("payments/", views.payments, name="payments"),
    path("reports/", views.reports, name="reports"),
]
