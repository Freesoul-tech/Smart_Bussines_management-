from django.urls import path

from .views import (
    business_setup,
    restaurant_dashboard,
    restaurant_order_detail,
    restaurant_order_create,
    restaurant_payment_create,
    restaurant_payments,
    restaurant_orders,
    restaurant_product_create,
    restaurant_product_delete,
    restaurant_product_edit,
    restaurant_products,
    restaurant_reservation_form,
    restaurant_reservations,
    restaurant_table_delete,
    restaurant_table_form,
    restaurant_tables,
)


app_name = "businesses"


urlpatterns = [
    path(
        "setup/",
        business_setup,
        name="business_setup",
    ),

    path(
        "restaurant/",
        restaurant_dashboard,
        name="restaurant_dashboard",
    ),
    path("restaurant/products/", restaurant_products, name="restaurant_products"),
    path("restaurant/products/add/", restaurant_product_create, name="restaurant_product_create"),
    path("restaurant/products/<int:item_id>/edit/", restaurant_product_edit, name="restaurant_product_edit"),
    path("restaurant/products/<int:item_id>/delete/", restaurant_product_delete, name="restaurant_product_delete"),
    path("restaurant/orders/", restaurant_orders, name="restaurant_orders"),
    path("restaurant/orders/add/", restaurant_order_create, name="restaurant_order_create"),
    path("restaurant/payments/", restaurant_payments, name="restaurant_payments"),
    path("restaurant/payments/add/", restaurant_payment_create, name="restaurant_payment_create"),
    path("restaurant/orders/<int:order_id>/", restaurant_order_detail, name="restaurant_order_detail"),
    path("restaurant/tables/", restaurant_tables, name="restaurant_tables"),
    path("restaurant/tables/add/", restaurant_table_form, name="restaurant_table_create"),
    path("restaurant/tables/<int:table_id>/edit/", restaurant_table_form, name="restaurant_table_edit"),
    path("restaurant/tables/<int:table_id>/delete/", restaurant_table_delete, name="restaurant_table_delete"),
    path("restaurant/reservations/", restaurant_reservations, name="restaurant_reservations"),
    path("restaurant/reservations/add/", restaurant_reservation_form, name="restaurant_reservation_create"),
    path("restaurant/reservations/<int:reservation_id>/edit/", restaurant_reservation_form, name="restaurant_reservation_edit"),
]
