from django import forms

from accounts.models import User
from businesses.models import (
    BakeryCategory,
    BakeryExpense,
    BakeryIngredient,
    BakeryOrder,
    BakeryProduction,
    BakeryProduct,
    BakeryProfile,
    BakeryRecipe,
    BakerySupplier,
)
from customers.models import Customer


class BakeryProductForm(forms.ModelForm):
    class Meta:
        model = BakeryProduct
        fields = ["category", "name", "description", "selling_price", "stock_quantity", "is_available"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = BakeryCategory.objects.filter(business=business)


class BakeryProfileForm(forms.ModelForm):
    class Meta:
        model = BakeryProfile
        fields = ["description", "phone", "email", "opening_time", "closing_time"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "opening_time": forms.TimeInput(attrs={"type": "time"}),
            "closing_time": forms.TimeInput(attrs={"type": "time"}),
        }


class BakeryIngredientForm(forms.ModelForm):
    class Meta:
        model = BakeryIngredient
        fields = ["supplier", "name", "quantity_in_stock", "unit", "minimum_stock", "is_active"]

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supplier"].queryset = BakerySupplier.objects.filter(business=business)


class BakerySupplierForm(forms.ModelForm):
    class Meta:
        model = BakerySupplier
        fields = ["name", "phone", "email", "address", "notes", "is_active"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)


class BakeryRecipeForm(forms.ModelForm):
    ingredient = forms.ModelChoiceField(queryset=BakeryIngredient.objects.none())
    required_quantity = forms.DecimalField(min_value=0.001, max_digits=12, decimal_places=3)

    class Meta:
        model = BakeryRecipe
        fields = ["product", "instructions"]
        widgets = {"instructions": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = BakeryProduct.objects.filter(business=business)
        self.fields["ingredient"].queryset = BakeryIngredient.objects.filter(business=business)


class BakeryProductionForm(forms.ModelForm):
    class Meta:
        model = BakeryProduction
        fields = ["product", "staff", "quantity_produced", "production_date", "status", "notes"]
        widgets = {
            "production_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = BakeryProduct.objects.filter(business=business)
        staff_ids = business.employees.filter(user__isnull=False).values_list("user_id", flat=True) if business else []
        self.fields["staff"].queryset = User.objects.filter(id__in=staff_ids)


class BakeryExpenseForm(forms.ModelForm):
    class Meta:
        model = BakeryExpense
        fields = ["category", "description", "amount", "expense_date", "notes"]
        widgets = {
            "expense_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)


class BakeryOrderForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=BakeryProduct.objects.none())
    quantity = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        model = BakeryOrder
        fields = ["customer", "status", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = BakeryProduct.objects.filter(business=business)
        self.fields["customer"].queryset = Customer.objects.filter(business=business)
