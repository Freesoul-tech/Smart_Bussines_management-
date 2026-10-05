
from django import forms

from .models import Reservation
from rooms.models import Room
from customers.models import Customer


class ReservationForm(forms.ModelForm):

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.none(),
        required=True,
        empty_label="Select a customer",
        widget=forms.Select(),
    )

    class Meta:
        model = Reservation

        fields = [
            "customer",
            "room",
            "check_in",
            "check_out",
            "number_of_guests",
            "status",
            "notes",
        ]

        widgets = {
            "room": forms.Select(),

            "check_in": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "check_out": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "number_of_guests": forms.NumberInput(
                attrs={
                    "min": "1",
                    "placeholder": "Number of guests",
                }
            ),

            "status": forms.Select(),

            "notes": forms.Textarea(
                attrs={
                    "placeholder": "Optional notes",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, business=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.business = business

        if business:

            # -------------------------------------------------
            # ONLY CUSTOMERS BELONGING TO THIS BUSINESS
            # -------------------------------------------------

            self.fields["customer"].queryset = (
                Customer.objects.filter(
                    business=business
                ).order_by("name")
            )

            # -------------------------------------------------
            # ONLY ROOMS BELONGING TO THIS BUSINESS
            # -------------------------------------------------

            self.fields["room"].queryset = (
                Room.objects.filter(
                    business=business
                ).order_by("room_number")
            )

        # -----------------------------------------------------
        # WHEN EDITING AN EXISTING RESERVATION
        # -----------------------------------------------------

        if self.instance and self.instance.pk:

            if self.instance.customer_id:

                self.initial["customer"] = (
                    self.instance.customer_id
                )

    def clean(self):

        cleaned_data = super().clean()

        customer = cleaned_data.get("customer")
        room = cleaned_data.get("room")
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        status = cleaned_data.get("status")

        # -------------------------------------------------
        # CUSTOMER VALIDATION
        # -------------------------------------------------

        if customer and self.business:

            if customer.business_id != self.business.id:

                raise forms.ValidationError(
                    "The selected customer does not belong "
                    "to this business."
                )

        # -------------------------------------------------
        # ROOM VALIDATION
        # -------------------------------------------------

        if room and self.business:

            if room.business_id != self.business.id:

                raise forms.ValidationError(
                    "The selected room does not belong "
                    "to this business."
                )

        # -------------------------------------------------
        # DATE VALIDATION
        # -------------------------------------------------

        if not room or not check_in or not check_out:

            return cleaned_data

        if check_out <= check_in:

            raise forms.ValidationError(
                "Check-out date must be after the check-in date."
            )

        # -------------------------------------------------
        # ROOM AVAILABILITY
        # -------------------------------------------------

        blocking_statuses = [
            "confirmed",
            "checked_in",
        ]

        if status in blocking_statuses:

            overlapping = Reservation.objects.filter(
                room=room,
                status__in=blocking_statuses,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )

            if self.instance.pk:

                overlapping = overlapping.exclude(
                    pk=self.instance.pk
                )

            if overlapping.exists():

                raise forms.ValidationError(
                    f"Room {room.room_number} is already "
                    "reserved during the selected dates."
                )

        return cleaned_data

    def save(self, commit=True):

        reservation = super().save(commit=False)

        customer = self.cleaned_data.get("customer")

        if customer:

            # -------------------------------------------------
            # COPY CUSTOMER INFORMATION INTO RESERVATION
            # -------------------------------------------------

            reservation.customer = customer

            reservation.customer_name = customer.name
            reservation.customer_phone = customer.phone
            reservation.customer_email = customer.email

        if commit:

            reservation.save()
            self.save_m2m()

        return reservation
