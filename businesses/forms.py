from django import forms
from payments.models import Payment

from .models import Business, Customer, MenuCategory, MenuItem, Order, Reservation, RestaurantTable


class BusinessSetupForm(forms.ModelForm):

    class Meta:
        model = Business

        fields = [
            "user_name",
            "position",
            "name",
            "location",
            "certificate",
            "business_model",
        ]

        widgets = {

            "user_name": forms.TextInput(
                attrs={
                    "placeholder": "Enter your name",
                    "class": "form-input",
                }
            ),

            "position": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Owner, Manager",
                    "class": "form-input",
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "placeholder": "Enter your business name",
                    "class": "form-input",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "placeholder": "Enter your business location",
                    "class": "form-input",
                    "autocomplete": "off",
                }
            ),

            "certificate": forms.ClearableFileInput(
                attrs={
                    "class": "form-file",
                }
            ),

            "business_model": forms.HiddenInput(),
        }

        labels = {
            "location": "Business Location",
        }

        help_texts = {
            "location": "",
        }


class MenuCategoryForm(forms.ModelForm):

    class Meta:
        model = MenuCategory
        fields = ["name", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }


class MenuItemForm(forms.ModelForm):

    class Meta:
        model = MenuItem
        fields = ["category", "name", "description", "price", "is_available"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-input"}),
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "price": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0"}),
        }


class OrderStatusForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-input"}),
        }


class RestaurantTableForm(forms.ModelForm):

    class Meta:
        model = RestaurantTable
        fields = ["table_number", "capacity", "status", "is_active"]
        widgets = {
            "table_number": forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. 12"}),
            "capacity": forms.NumberInput(attrs={"class": "form-input", "min": "1"}),
            "status": forms.Select(attrs={"class": "form-input"}),
        }


class RestaurantReservationForm(forms.ModelForm):

    class Meta:
        model = Reservation
        fields = ["customer", "table", "reservation_date", "reservation_time", "number_of_guests", "status", "notes"]
        widgets = {
            "customer": forms.Select(attrs={"class": "form-input"}),
            "table": forms.Select(attrs={"class": "form-input"}),
            "reservation_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "reservation_time": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "number_of_guests": forms.NumberInput(attrs={"class": "form-input", "min": "1"}),
            "status": forms.Select(attrs={"class": "form-input"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }

    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Customer.objects.filter(restaurant=restaurant)
        self.fields["table"].queryset = RestaurantTable.objects.filter(restaurant=restaurant, is_active=True)


class RestaurantOrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ["table", "customer", "payment_method", "notes"]
        widgets = {
            "table": forms.Select(attrs={"class": "form-input"}),
            "customer": forms.Select(attrs={"class": "form-input"}),
            "payment_method": forms.Select(attrs={"class": "form-input"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }

    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["table"].queryset = RestaurantTable.objects.filter(restaurant=restaurant, is_active=True)
        self.fields["customer"].queryset = Customer.objects.filter(restaurant=restaurant)


class RestaurantPaymentForm(forms.Form):
    order = forms.ModelChoiceField(queryset=Order.objects.none(), widget=forms.Select(attrs={"class": "form-input"}))
    reservation = forms.ModelChoiceField(queryset=Reservation.objects.none(), required=False, widget=forms.Select(attrs={"class": "form-input"}))
    amount = forms.DecimalField(min_value=0.01, decimal_places=2, max_digits=12, widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}))
    payment_method = forms.ChoiceField(choices=[], widget=forms.Select(attrs={"class": "form-input"}))
    reference = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-input"}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-input", "rows": 3}))

    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order"].queryset = Order.objects.filter(restaurant=restaurant).prefetch_related("items__menu_item")
        self.fields["reservation"].queryset = Reservation.objects.filter(restaurant=restaurant).exclude(status="cancelled")
        self.fields["payment_method"].choices = Payment.PAYMENT_METHODS
