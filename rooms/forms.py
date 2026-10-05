from django import forms

from .models import Room


class RoomForm(forms.ModelForm):

    class Meta:
        model = Room

        fields = [
            "room_number",
            "room_type",
            "floor",
            "price_per_night",
            "status",
        ]

        widgets = {
            "room_number": forms.TextInput(
                attrs={
                    "placeholder": "e.g. 101",
                }
            ),

            "room_type": forms.Select(),

            "floor": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Ground Floor, 1st Floor",
                }
            ),

            "price_per_night": forms.NumberInput(
                attrs={
                    "placeholder": "Enter price per night",
                    "step": "0.01",
                }
            ),

            "status": forms.Select(),
        }
        