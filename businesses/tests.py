from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import (
	BakeryCategory,
	BakeryIngredient,
	BakeryOrder,
	BakeryOrderItem,
	BakeryProduct,
	BakeryRecipe,
	BakeryRecipeIngredient,
	BakerySupplier,
	Business,
)


class BakeryModelTests(TestCase):

	def setUp(self):
		user = get_user_model().objects.create_user(
			username="bakery-owner",
			password="test-password",
		)
		self.business = Business.objects.create(
			owner=user,
			name="Test Bakery",
			business_model="bakery",
		)

	def test_bakery_recipe_and_order_totals(self):
		category = BakeryCategory.objects.create(
			business=self.business,
			name="Cakes",
		)
		product = BakeryProduct.objects.create(
			business=self.business,
			category=category,
			name="Chocolate Cake",
			selling_price=Decimal("25.00"),
		)
		supplier = BakerySupplier.objects.create(
			business=self.business,
			name="Local Foods",
		)
		ingredient = BakeryIngredient.objects.create(
			business=self.business,
			supplier=supplier,
			name="Flour",
			quantity_in_stock=Decimal("2.000"),
			minimum_stock=Decimal("5.000"),
		)
		recipe = BakeryRecipe.objects.create(product=product)
		recipe_ingredient = BakeryRecipeIngredient.objects.create(
			recipe=recipe,
			ingredient=ingredient,
			required_quantity=Decimal("0.500"),
		)
		order = BakeryOrder.objects.create(business=self.business)
		item = BakeryOrderItem.objects.create(
			order=order,
			product=product,
			quantity=2,
			unit_price=product.selling_price,
		)

		self.assertEqual(recipe_ingredient.required_quantity, Decimal("0.500"))
		self.assertTrue(ingredient.is_low_stock)
		self.assertEqual(item.subtotal, Decimal("50.00"))
		self.assertEqual(order.total_amount, Decimal("50.00"))
