from django import forms

from .models import Customer


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer

        fields = [
            "name",
            "phone",
            "email",
            "address",
            "notes",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Customer name",
                    "class": "form-input",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Phone number",
                    "class": "form-input",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email address",
                    "class": "form-input",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "placeholder": "Address",
                    "class": "form-input",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "placeholder": "Additional notes",
                    "class": "form-input",
                    "rows": 4,
                }
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if phone:
            phone = phone.strip()

        return phone