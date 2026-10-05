from decimal import Decimal

from django.db import models
from django.conf import settings


BUSINESS_MODELS = [
    ("hotel", "Hotel"),
    ("motel", "Motel"),
    ("lodge", "Lodge"),
    ("guest_house", "Guest House"),
    ("restaurant", "Restaurant"),
    ("bakery", "Bakery"),
    ("pub_bar", "Pub / Bar"),
    ("boutique", "Boutique"),
]


class Business(models.Model):

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    user_name = models.CharField(
        max_length=150,
        blank=True,
    )

    position = models.CharField(
        max_length=100,
        blank=True,
    )

    name = models.CharField(
        max_length=200,
    )
    location = models.CharField(
    max_length=255,
    blank=True,
    )

    latitude = models.DecimalField(
    max_digits=9,
    decimal_places=6,
    null=True,
    blank=True,
    )

    longitude = models.DecimalField(
    max_digits=9,
    decimal_places=6,
    null=True,
    blank=True,
    )

    certificate = models.FileField(
        upload_to="certificates/",
        blank=True,
        null=True,
    )

    business_model = models.CharField(
        max_length=50,
        choices=BUSINESS_MODELS,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name


# ============================================================
# RESTAURANT
# ============================================================

class Restaurant(models.Model):

    business = models.OneToOneField(
        Business,
        on_delete=models.CASCADE,
        related_name="restaurant",
    )

    description = models.TextField(
        blank=True,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    opening_time = models.TimeField(
        null=True,
        blank=True,
    )

    closing_time = models.TimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.business.name


class MenuCategory(models.Model):

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="menu_categories",
    )

    name = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name_plural = "Menu Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class MenuItem(models.Model):

    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.CASCADE,
        related_name="items",
    )

    name = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    is_available = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RestaurantTable(models.Model):

    STATUS_CHOICES = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("reserved", "Reserved"),
        ("maintenance", "Maintenance"),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="tables",
    )

    table_number = models.CharField(
        max_length=20,
    )

    capacity = models.PositiveIntegerField(
        default=2,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["table_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "table_number"],
                name="unique_restaurant_table_number",
            ),
        ]

    def __str__(self):
        return f"Table {self.table_number}"


class Customer(models.Model):

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="customers",
    )

    name = models.CharField(
        max_length=150,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name


class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("served", "Served"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_CHOICES = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("mobile_money", "Mobile Money"),
        ("other", "Other"),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Order #{self.id}"

    @property
    def total_amount(self):
        return sum(
            item.subtotal for item in self.items.all()
        )


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"


class Reservation(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("seated", "Seated"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="reservations",
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="reservations",
    )

    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservations",
    )

    reservation_date = models.DateField()

    reservation_time = models.TimeField()

    number_of_guests = models.PositiveIntegerField(
        default=1,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.customer.name} - "
            f"{self.reservation_date} "
            f"{self.reservation_time}"
        )


# ============================================================
# BAKERY
# ============================================================

class BakeryProfile(models.Model):

    business = models.OneToOneField(
        Business,
        on_delete=models.CASCADE,
        related_name="bakery_profile",
    )

    description = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.business.name


class BakeryCategory(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="bakery_categories",
    )

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "name"],
                name="unique_bakery_category_name",
            ),
        ]

    def __str__(self):
        return self.name


class BakeryProduct(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="bakery_products",
    )

    category = models.ForeignKey(
        BakeryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "name"],
                name="unique_bakery_product_name",
            ),
        ]

    def __str__(self):
        return self.name


class BakerySupplier(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="bakery_suppliers",
    )

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "name"],
                name="unique_bakery_supplier_name",
            ),
        ]

    def __str__(self):
        return self.name


class BakeryIngredient(models.Model):

    UNIT_CHOICES = [
        ("kg", "Kilograms"),
        ("g", "Grams"),
        ("l", "Litres"),
        ("ml", "Millilitres"),
        ("unit", "Units"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="bakery_ingredients",
    )

    supplier = models.ForeignKey(
        BakerySupplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ingredients",
    )
    name = models.CharField(max_length=150)
    quantity_in_stock = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="kg")
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "name"],
                name="unique_bakery_ingredient_name",
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.minimum_stock


class BakeryRecipe(models.Model):

    product = models.OneToOneField(
        BakeryProduct,
        on_delete=models.CASCADE,
        related_name="recipe",
    )
    instructions = models.TextField(blank=True)

    def __str__(self):
        return f"Recipe for {self.product.name}"


class BakeryRecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        BakeryRecipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
    )
    ingredient = models.ForeignKey(
        BakeryIngredient,
        on_delete=models.PROTECT,
        related_name="recipe_usages",
    )
    required_quantity = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_bakery_recipe_ingredient",
            ),
        ]

    def __str__(self):
        return f"{self.ingredient.name} for {self.recipe.product.name}"


class BakeryProduction(models.Model):

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="bakery_production",
    )
    product = models.ForeignKey(
        BakeryProduct,
        on_delete=models.PROTECT,
        related_name="production_batches",
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bakery_production_batches",
    )
    quantity_produced = models.DecimalField(max_digits=12, decimal_places=3)
    production_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-production_date", "-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.quantity_produced}"


class BakeryStockMovement(models.Model):

    MOVEMENT_TYPES = [
        ("production", "Production"),
        ("sale", "Sale"),
        ("adjustment", "Adjustment"),
        ("waste", "Waste"),
    ]

    product = models.ForeignKey(
        BakeryProduct,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    ingredient = models.ForeignKey(
        BakeryIngredient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        item = self.product or self.ingredient
        return f"{item} - {self.quantity}"


class BakeryOrder(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="bakery_orders",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bakery_orders",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def total_amount(self):
        return sum((item.subtotal for item in self.items.all()), Decimal("0.00"))

    def __str__(self):
        return f"Bakery Order #{self.id}"


class BakeryOrderItem(models.Model):

    order = models.ForeignKey(
        BakeryOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        BakeryProduct,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class BakeryExpense(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="bakery_expenses",
    )
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-expense_date", "-created_at"]

    def __str__(self):
        return f"{self.category} - {self.amount}"


# ============================================================
# PUB / BAR
# ============================================================

class PubBarProfile(models.Model):

    business = models.OneToOneField(
        Business,
        on_delete=models.CASCADE,
        related_name="pub_bar_profile",
    )
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.business.name


class PubBarTable(models.Model):

    STATUS_CHOICES = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("reserved", "Reserved"),
        ("maintenance", "Maintenance"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="pub_bar_tables",
    )
    table_number = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField(default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["table_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "table_number"],
                name="unique_pub_bar_table_number",
            ),
        ]

    def __str__(self):
        return f"Table {self.table_number}"


class PubBarCategory(models.Model):

    CATEGORY_CHOICES = [
        ("beer", "Beers"),
        ("wine", "Wines"),
        ("spirit", "Spirits"),
        ("cocktail", "Cocktails"),
        ("soft_drink", "Soft Drinks"),
        ("other", "Other"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="pub_bar_categories",
    )
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "name"],
                name="unique_pub_bar_category_name",
            ),
        ]

    def __str__(self):
        return self.name


class PubBarProduct(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="pub_bar_products",
    )
    category = models.ForeignKey(
        PubBarCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "name"],
                name="unique_pub_bar_product_name",
            ),
        ]

    def __str__(self):
        return self.name


class PubBarSupplier(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="pub_bar_suppliers",
    )
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "name"],
                name="unique_pub_bar_supplier_name",
            ),
        ]

    def __str__(self):
        return self.name


class PubBarInventoryMovement(models.Model):

    MOVEMENT_TYPES = [
        ("stock_in", "Stock In"),
        ("stock_out", "Stock Out"),
        ("adjustment", "Adjustment"),
    ]

    product = models.ForeignKey(
        PubBarProduct,
        on_delete=models.CASCADE,
        related_name="inventory_movements",
    )
    supplier = models.ForeignKey(
        PubBarSupplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_movements",
    )
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class PubBarOrder(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("served", "Served"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="pub_bar_orders",
    )
    table = models.ForeignKey(
        PubBarTable,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pub_bar_orders",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def total_amount(self):
        return sum((item.subtotal for item in self.items.all()), Decimal("0.00"))

    def __str__(self):
        return f"Pub/Bar Order #{self.id}"


class PubBarOrderItem(models.Model):

    order = models.ForeignKey(
        PubBarOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        PubBarProduct,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class PubBarReservation(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="pub_bar_reservations",
    )
    table = models.ForeignKey(PubBarTable, on_delete=models.CASCADE, related_name="reservations")
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="pub_bar_reservations")
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    number_of_guests = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-reservation_date", "-reservation_time"]

    def __str__(self):
        return f"{self.customer.name} - {self.reservation_date}"


# ============================================================
# BOUTIQUE
# ============================================================

class BoutiqueProfile(models.Model):

    business = models.OneToOneField(
        Business,
        on_delete=models.CASCADE,
        related_name="boutique_profile",
    )
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.business.name


class BoutiqueCategory(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="boutique_categories",
    )
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "name"],
                name="unique_boutique_category_name",
            ),
        ]

    def __str__(self):
        return self.name


class BoutiqueProduct(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="boutique_products",
    )
    category = models.ForeignKey(
        BoutiqueCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "name"],
                name="unique_boutique_product_name",
            ),
            models.UniqueConstraint(
                fields=["business", "sku"],
                condition=~models.Q(sku=""),
                name="unique_boutique_product_sku",
            ),
        ]

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.minimum_stock

    def __str__(self):
        return self.name


class BoutiqueInventoryMovement(models.Model):

    MOVEMENT_TYPES = [
        ("stock_in", "Stock In"),
        ("stock_out", "Stock Out"),
        ("adjustment", "Adjustment"),
    ]

    product = models.ForeignKey(
        BoutiqueProduct,
        on_delete=models.CASCADE,
        related_name="inventory_movements",
    )
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class BoutiqueOrder(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="boutique_orders",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="boutique_orders",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def total_amount(self):
        return sum((item.subtotal for item in self.items.all()), Decimal("0.00"))

    def __str__(self):
        return f"Boutique Sale #{self.id}"


class BoutiqueOrderItem(models.Model):

    order = models.ForeignKey(
        BoutiqueOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        BoutiqueProduct,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


