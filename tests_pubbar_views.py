from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from businesses.models import (
    Business,
    PubBarInventoryMovement,
    PubBarOrder,
    PubBarProduct,
    PubBarTable,
)
from payments.models import Payment


class PubBarViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="pub-view-owner",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=user,
            name="View Pub",
            business_model="pub_bar",
        )
        self.client.force_login(user)

    def test_pub_bar_navigation_and_stock_order_workflow(self):
        self.assertEqual(self.client.get(reverse("pub_bar:dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("pub_bar:products_add")).status_code, 200)
        self.assertEqual(self.client.get(reverse("pub_bar:suppliers")).status_code, 200)

        product_response = self.client.post(reverse("pub_bar:products_add"), {
            "name": "Tonic",
            "description": "Soft drink",
            "selling_price": "2.50",
            "stock_quantity": "0",
            "is_available": "on",
        })
        self.assertEqual(product_response.status_code, 302)
        product = PubBarProduct.objects.get(business=self.business, name="Tonic")

        inventory_response = self.client.post(reverse("pub_bar:inventory_add"), {
            "product": product.id,
            "movement_type": "stock_in",
            "quantity": "10",
            "notes": "Opening stock",
        })
        self.assertEqual(inventory_response.status_code, 302)
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, Decimal("10.000"))
        self.assertEqual(PubBarInventoryMovement.objects.count(), 1)

        order_response = self.client.post(reverse("pub_bar:orders_add"), {
            "quantity": "2",
            "status": "pending",
            "notes": "Table service",
        })
        self.assertEqual(order_response.status_code, 200)
        self.assertEqual(PubBarOrder.objects.count(), 0)

        table_response = self.client.post(reverse("pub_bar:tables_add"), {
            "table_number": "1",
            "capacity": "4",
            "status": "available",
            "is_active": "on",
        })
        self.assertEqual(table_response.status_code, 302)
        self.assertEqual(PubBarTable.objects.count(), 1)

        order_response = self.client.post(reverse("pub_bar:orders_add"), {
            "product": product.id,
            "quantity": "2",
            "status": "completed",
            "notes": "Table service",
        })
        self.assertEqual(order_response.status_code, 302)
        order = PubBarOrder.objects.get(business=self.business)

        payment_response = self.client.post(reverse("pub_bar:payment_add"), {
            "pub_bar_order": order.id,
            "amount": "5.00",
            "payment_method": "cash",
            "status": "paid",
            "reference": "CASH-1",
            "notes": "Paid at table",
        })
        self.assertEqual(payment_response.status_code, 302)
        self.assertTrue(Payment.objects.filter(pub_bar_order=order).exists())
