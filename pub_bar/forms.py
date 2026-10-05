from django import forms

from accounts.models import User
from businesses.models import (
    PubBarCategory,
    PubBarInventoryMovement,
    PubBarOrder,
    PubBarProduct,
    PubBarProfile,
    PubBarReservation,
    PubBarSupplier,
    PubBarTable,
)
from customers.models import Customer
from payments.models import Payment


class PubBarProfileForm(forms.ModelForm):
    class Meta:
        model = PubBarProfile
        fields = ["description", "phone", "email", "opening_time", "closing_time"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4}), "opening_time": forms.TimeInput(attrs={"type": "time"}), "closing_time": forms.TimeInput(attrs={"type": "time"})}


class PubBarCategoryForm(forms.ModelForm):
    class Meta:
        model = PubBarCategory
        fields = ["name", "category_type", "is_active"]

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)


class PubBarProductForm(forms.ModelForm):
    class Meta:
        model = PubBarProduct
        fields = ["category", "name", "description", "selling_price", "stock_quantity", "is_available"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = PubBarCategory.objects.filter(business=business)


class PubBarTableForm(forms.ModelForm):
    class Meta:
        model = PubBarTable
        fields = ["table_number", "capacity", "status", "is_active"]

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)


class PubBarSupplierForm(forms.ModelForm):
    class Meta:
        model = PubBarSupplier
        fields = ["name", "phone", "email", "address", "notes", "is_active"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)


class PubBarInventoryForm(forms.ModelForm):
    class Meta:
        model = PubBarInventoryMovement
        fields = ["product", "supplier", "movement_type", "quantity", "notes"]

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = PubBarProduct.objects.filter(business=business)
        self.fields["supplier"].queryset = PubBarSupplier.objects.filter(business=business)


class PubBarOrderForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=PubBarProduct.objects.none())
    quantity = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        model = PubBarOrder
        fields = ["table", "customer", "status", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = PubBarProduct.objects.filter(business=business, is_available=True)
        self.fields["table"].queryset = PubBarTable.objects.filter(business=business, is_active=True)
        self.fields["customer"].queryset = Customer.objects.filter(business=business)


class PubBarReservationForm(forms.ModelForm):
    class Meta:
        model = PubBarReservation
        fields = ["table", "customer", "reservation_date", "reservation_time", "number_of_guests", "status", "notes"]
        widgets = {"reservation_date": forms.DateInput(attrs={"type": "date"}), "reservation_time": forms.TimeInput(attrs={"type": "time"}), "notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["table"].queryset = PubBarTable.objects.filter(business=business, is_active=True)
        self.fields["customer"].queryset = Customer.objects.filter(business=business)


class PubBarPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["pub_bar_order", "amount", "payment_method", "status", "reference", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pub_bar_order"].queryset = PubBarOrder.objects.filter(business=business)

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount
