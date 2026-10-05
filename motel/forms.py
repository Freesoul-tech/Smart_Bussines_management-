from django import forms

from customers.models import Customer
from reservations.models import Reservation

from .models import ParkingSpace, Vehicle


class VehicleForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset=Customer.objects.none(), required=False)
    reservation = forms.ModelChoiceField(queryset=Reservation.objects.none(), required=False)

    class Meta:
        model = Vehicle
        fields = ["registration_number", "vehicle_type", "description", "customer", "reservation"]

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = business
        if business:
            self.fields["customer"].queryset = Customer.objects.filter(business=business)
            self.fields["reservation"].queryset = Reservation.objects.filter(business=business).select_related("room")

    def clean(self):
        cleaned_data = super().clean()
        business = getattr(self, "business", None)
        customer = cleaned_data.get("customer")
        reservation = cleaned_data.get("reservation")
        if business and customer and customer.business_id != business.id:
            raise forms.ValidationError("The selected customer does not belong to this business.")
        if business and reservation and reservation.business_id != business.id:
            raise forms.ValidationError("The selected reservation does not belong to this business.")
        return cleaned_data


class ParkingSpaceForm(forms.ModelForm):
    class Meta:
        model = ParkingSpace
        fields = ["space_number", "status"]
