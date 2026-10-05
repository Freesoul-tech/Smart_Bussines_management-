from django import forms

from .models import Payment
from reservations.models import Reservation


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment

        fields = [
            "reservation",
            "amount",
            "payment_method",
            "status",
            "reference",
            "notes",
        ]

        widgets = {
            "reservation": forms.Select(),

            "amount": forms.NumberInput(
                attrs={
                    "placeholder": "Enter payment amount",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "payment_method": forms.Select(),

            "status": forms.Select(),

            "reference": forms.TextInput(
                attrs={
                    "placeholder": "Payment reference (optional)",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "placeholder": "Optional notes",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        business = kwargs.pop("business", None)

        super().__init__(*args, **kwargs)

        if business:

            self.fields["reservation"].queryset = (
                Reservation.objects.filter(
                    business=business
                )
                .exclude(status="cancelled")
                .order_by("-check_in")
            )

    def clean_amount(self):

        amount = self.cleaned_data.get("amount")

        if amount is not None and amount <= 0:
            raise forms.ValidationError(
                "Payment amount must be greater than zero."
            )

        return amount