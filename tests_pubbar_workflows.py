from datetime import date, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from businesses.models import (
    Business,
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
from customers.models import Customer
from payments.models import Payment


class PubBarModelTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="pub-owner",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=user,
            name="Test Pub",
            business_model="pub_bar",
        )
        self.customer = Customer.objects.create(
            business=self.business,
            name="Regular Guest",
            phone="0999000000",
        )

    def test_pub_bar_sales_reservations_inventory_and_payment(self):
        profile = PubBarProfile.objects.create(
            business=self.business,
            description="Evening drinks and live music",
        )
        category = PubBarCategory.objects.create(
            business=self.business,
            name="Beers",
            category_type="beer",
        )
        product = PubBarProduct.objects.create(
            business=self.business,
            category=category,
            name="Local Lager",
            selling_price=Decimal("4.50"),
            stock_quantity=Decimal("20.000"),
        )
        supplier = PubBarSupplier.objects.create(
            business=self.business,
            name="Beverage Supplier",
        )
        table = PubBarTable.objects.create(
            business=self.business,
            table_number="T1",
            capacity=4,
        )
        reservation = PubBarReservation.objects.create(
            business=self.business,
            table=table,
            customer=self.customer,
            reservation_date=date.today(),
            reservation_time=time(19, 0),
            number_of_guests=2,
        )
        order = PubBarOrder.objects.create(
            business=self.business,
            table=table,
            customer=self.customer,
        )
        item = PubBarOrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            unit_price=product.selling_price,
        )
        movement = PubBarInventoryMovement.objects.create(
            product=product,
            supplier=supplier,
            movement_type="stock_in",
            quantity=Decimal("12.000"),
        )
        payment = Payment.objects.create(
            business=self.business,
            pub_bar_order=order,
            amount=order.total_amount,
        )

        self.assertEqual(profile.business_id, self.business.id)
        self.assertEqual(reservation.table_id, table.id)
        self.assertEqual(item.subtotal, Decimal("9.00"))
        self.assertEqual(order.total_amount, Decimal("9.00"))
        self.assertEqual(movement.get_movement_type_display(), "Stock In")
        self.assertEqual(str(payment), f"Pub/Bar Order #{order.id} - 9.00")
