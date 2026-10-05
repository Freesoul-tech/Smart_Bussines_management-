from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from businesses.models import (
    BoutiqueCategory,
    BoutiqueInventoryMovement,
    BoutiqueOrder,
    BoutiqueOrderItem,
    BoutiqueProduct,
    Business,
)
from customers.models import Customer
from payments.models import Payment


class BoutiqueWorkflowTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="boutique-owner", password="test-password")
        self.client.login(username="boutique-owner", password="test-password")
        self.business = Business.objects.create(owner=user, name="Test Boutique", business_model="boutique")
        self.customer = Customer.objects.create(business=self.business, name="Regular Customer")
        self.category = BoutiqueCategory.objects.create(business=self.business, name="Accessories")
        self.product = BoutiqueProduct.objects.create(
            business=self.business,
            category=self.category,
            name="Leather Bag",
            sku="BAG-001",
            selling_price=Decimal("40.00"),
            stock_quantity=Decimal("5.000"),
            minimum_stock=Decimal("1.000"),
        )

    def test_sale_reduces_stock_and_calculates_total(self):
        response = self.client.post(reverse("boutique:sales"), {
            "product": self.product.id,
            "quantity": 2,
            "customer": self.customer.id,
            "status": "completed",
            "notes": "Gift wrap",
        })
        self.assertRedirects(response, reverse("boutique:sales"))
        self.product.refresh_from_db()
        order = BoutiqueOrder.objects.get(business=self.business)
        self.assertEqual(self.product.stock_quantity, Decimal("3.000"))
        self.assertEqual(order.total_amount, Decimal("80.00"))
        self.assertEqual(order.items.count(), 1)

    def test_categories_page_renders(self):
        response = self.client.get(reverse("boutique:categories"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Categories")

    def test_inventory_stock_out_rejects_negative_stock(self):
        response = self.client.post(reverse("boutique:inventory_add"), {
            "product": self.product.id,
            "movement_type": "stock_out",
            "quantity": "8.000",
            "notes": "Invalid adjustment",
        })
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, Decimal("5.000"))
        self.assertFalse(BoutiqueInventoryMovement.objects.exists())

    def test_payment_is_linked_to_boutique_sale(self):
        order = BoutiqueOrder.objects.create(business=self.business, customer=self.customer)
        BoutiqueOrderItem.objects.create(order=order, product=self.product, quantity=1, unit_price=self.product.selling_price)
        response = self.client.post(reverse("boutique:payments"), {
            "boutique_order": order.id,
            "amount": "40.00",
            "payment_method": "card",
            "status": "paid",
            "reference": "CARD-1",
            "notes": "",
        })
        self.assertRedirects(response, reverse("boutique:payments"))
        payment = Payment.objects.get(boutique_order=order)
        self.assertEqual(str(payment), f"Boutique Sale #{order.id} - 40.00")
