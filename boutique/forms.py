from django import forms

from businesses.models import (
    BoutiqueCategory,
    BoutiqueInventoryMovement,
    BoutiqueOrder,
    BoutiqueProduct,
    BoutiqueProfile,
)
from customers.models import Customer
from payments.models import Payment


class BoutiqueProfileForm(forms.ModelForm):
    class Meta:
        model = BoutiqueProfile
        fields = ["description", "phone", "email", "opening_time", "closing_time"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "opening_time": forms.TimeInput(attrs={"type": "time"}),
            "closing_time": forms.TimeInput(attrs={"type": "time"}),
        }


class BoutiqueCategoryForm(forms.ModelForm):
    class Meta:
        model = BoutiqueCategory
        fields = ["name", "is_active"]

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)


class BoutiqueProductForm(forms.ModelForm):
    class Meta:
        model = BoutiqueProduct
        fields = [
            "category", "name", "sku", "description", "selling_price",
            "stock_quantity", "minimum_stock", "is_available",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = BoutiqueCategory.objects.filter(business=business)


class BoutiqueInventoryForm(forms.ModelForm):
    class Meta:
        model = BoutiqueInventoryMovement
        fields = ["product", "movement_type", "quantity", "notes"]

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = BoutiqueProduct.objects.filter(business=business)


class BoutiqueOrderForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=BoutiqueProduct.objects.none())
    quantity = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        model = BoutiqueOrder
        fields = ["customer", "status", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = BoutiqueProduct.objects.filter(
            business=business, is_available=True
        )
        self.fields["customer"].queryset = Customer.objects.filter(business=business)


class BoutiquePaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["boutique_order", "amount", "payment_method", "status", "reference", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["boutique_order"].queryset = BoutiqueOrder.objects.filter(business=business)

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount
