from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from businesses.models import (
    BakeryIngredient,
    BakeryOrder,
    BakeryProduction,
    BakeryProduct,
    BakeryProfile,
    BakeryRecipe,
    BakeryRecipeIngredient,
    BakeryStockMovement,
    BakerySupplier,
    Business,
)


class BakeryWorkflowTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="workflow-owner",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=user,
            name="Workflow Bakery",
            business_model="bakery",
        )
        self.client.force_login(user)

    def test_bakery_records_can_be_created(self):
        profile_response = self.client.post(reverse("bakery:profile"), {
            "description": "Fresh daily baking",
            "phone": "0999111222",
            "email": "bakery@example.com",
            "opening_time": "07:00",
            "closing_time": "18:00",
        })
        self.assertEqual(profile_response.status_code, 302)
        self.assertTrue(BakeryProfile.objects.filter(business=self.business).exists())

        product_response = self.client.post(reverse("bakery:product_add"), {
            "name": "Bread",
            "description": "Fresh bread",
            "selling_price": "5.00",
            "stock_quantity": "10",
            "is_available": "on",
        })
        self.assertEqual(product_response.status_code, 302)
        product = BakeryProduct.objects.get(business=self.business, name="Bread")

        supplier_response = self.client.post(reverse("bakery:supplier_add"), {
            "name": "Mill Supplier",
            "phone": "0999000000",
            "email": "mill@example.com",
            "address": "Town",
            "notes": "Flour supplier",
            "is_active": "on",
        })
        self.assertEqual(supplier_response.status_code, 302)
        supplier = BakerySupplier.objects.get(business=self.business)

        ingredient = BakeryIngredient.objects.create(
            business=self.business,
            supplier=supplier,
            name="Flour",
            quantity_in_stock=Decimal("20.000"),
            minimum_stock=Decimal("5.000"),
        )

        recipe_response = self.client.post(reverse("bakery:recipe_add"), {
            "product": product.id,
            "ingredient": ingredient.id,
            "required_quantity": "0.500",
            "instructions": "Mix and bake",
        })
        self.assertEqual(recipe_response.status_code, 302)
        self.assertTrue(BakeryRecipe.objects.filter(product=product).exists())

        production_response = self.client.post(reverse("bakery:production_add"), {
            "product": product.id,
            "quantity_produced": "12",
            "production_date": date.today().isoformat(),
            "status": "completed",
            "notes": "Morning batch",
        })
        self.assertEqual(production_response.status_code, 302)
        production = BakeryProduction.objects.get(product=product)
        product.refresh_from_db()
        ingredient.refresh_from_db()
        self.assertEqual(product.stock_quantity, Decimal("22.000"))
        self.assertEqual(ingredient.quantity_in_stock, Decimal("14.000"))
        self.assertEqual(
            BakeryStockMovement.objects.filter(movement_type="production").count(),
            2,
        )
        self.assertEqual(
            BakeryRecipeIngredient.objects.get(recipe=product.recipe).required_quantity,
            Decimal("0.500"),
        )

        completed_edit = self.client.post(
            reverse("bakery:production_edit", args=[production.id]),
            {
                "product": product.id,
                "quantity_produced": "99",
                "production_date": date.today().isoformat(),
                "status": "completed",
                "notes": "Should not change",
            },
        )
        self.assertEqual(completed_edit.status_code, 200)
        production.refresh_from_db()
        self.assertEqual(production.quantity_produced, Decimal("12.000"))

        expense_response = self.client.post(reverse("bakery:expense_add"), {
            "category": "Utilities",
            "description": "Electricity",
            "amount": "25.00",
            "expense_date": date.today().isoformat(),
            "notes": "Monthly bill",
        })
        self.assertEqual(expense_response.status_code, 302)

        order_response = self.client.post(reverse("bakery:order_add"), {
            "product": product.id,
            "quantity": "2",
            "status": "pending",
            "notes": "Customer pickup",
        })
        self.assertEqual(order_response.status_code, 302)
        self.assertEqual(BakeryOrder.objects.filter(business=self.business).count(), 1)
        self.assertEqual(ingredient.business_id, self.business.id)

    def test_insufficient_ingredients_do_not_create_or_change_stock(self):
        product = BakeryProduct.objects.create(
            business=self.business,
            name="Shortcake",
            selling_price=Decimal("8.00"),
        )
        ingredient = BakeryIngredient.objects.create(
            business=self.business,
            name="Butter",
            quantity_in_stock=Decimal("1.000"),
            minimum_stock=Decimal("0.000"),
        )
        recipe = BakeryRecipe.objects.create(product=product)
        BakeryRecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            required_quantity=Decimal("0.500"),
        )

        response = self.client.post(reverse("bakery:production_add"), {
            "product": product.id,
            "quantity_produced": "3",
            "production_date": date.today().isoformat(),
            "status": "completed",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(BakeryProduction.objects.filter(product=product).exists())
        ingredient.refresh_from_db()
        product.refresh_from_db()
        self.assertEqual(ingredient.quantity_in_stock, Decimal("1.000"))
        self.assertEqual(product.stock_quantity, Decimal("0.000"))
        self.assertFalse(BakeryStockMovement.objects.exists())
