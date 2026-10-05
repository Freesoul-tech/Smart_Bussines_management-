from django import forms

from .models import Employee


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee

        fields = [
            "first_name",
            "last_name",
            "position",
            "phone",
            "email",
            "employment_status",
            "date_joined",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "Enter first name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Enter last name",
                }
            ),

            "position": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Manager, Receptionist",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Enter phone number",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Enter email address",
                }
            ),

            "employment_status": forms.Select(),

            "date_joined": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }