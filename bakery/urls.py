from django.urls import path

from . import views


app_name = "bakery"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("products/", views.section_list, {"section": "products"}, name="products"),
    path("products/add/", views.product_form, name="product_add"),
    path("products/<int:object_id>/edit/", views.product_form, name="product_edit"),
    path("ingredients/", views.section_list, {"section": "ingredients"}, name="ingredients"),
    path("ingredients/add/", views.ingredient_form, name="ingredient_add"),
    path("ingredients/<int:object_id>/edit/", views.ingredient_form, name="ingredient_edit"),
    path("recipes/", views.section_list, {"section": "recipes"}, name="recipes"),
    path("recipes/add/", views.recipe_form, name="recipe_add"),
    path("recipes/<int:object_id>/edit/", views.recipe_form, name="recipe_edit"),
    path("production/", views.section_list, {"section": "production"}, name="production"),
    path("production/add/", views.production_form, name="production_add"),
    path("production/<int:object_id>/edit/", views.production_form, name="production_edit"),
    path("orders/", views.section_list, {"section": "orders"}, name="orders"),
    path("orders/add/", views.order_form, name="order_add"),
    path("suppliers/", views.section_list, {"section": "suppliers"}, name="suppliers"),
    path("suppliers/add/", views.supplier_form, name="supplier_add"),
    path("suppliers/<int:object_id>/edit/", views.supplier_form, name="supplier_edit"),
    path("expenses/", views.section_list, {"section": "expenses"}, name="expenses"),
    path("expenses/add/", views.expense_form, name="expense_add"),
    path("expenses/<int:object_id>/edit/", views.expense_form, name="expense_edit"),
    path("inventory/", views.section_list, {"section": "inventory"}, name="inventory"),
    path("reports/", views.reports, name="reports"),
]
