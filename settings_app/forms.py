from django import forms

from accounts.models import User
from employees.models import Employee


PERMISSION_OPTIONS = {
    "Employees": [
        ("employees.view_employee", "View employees"),
        ("employees.add_employee", "Add employees"),
        ("employees.change_employee", "Change employees"),
        ("employees.delete_employee", "Remove employees"),
    ],
    "Rooms": [
        ("rooms.view_room", "View rooms"),
        ("rooms.add_room", "Add rooms"),
        ("rooms.change_room", "Change rooms"),
        ("rooms.delete_room", "Remove rooms"),
    ],
    "Reservations": [
        ("reservations.view_reservation", "View reservations"),
        ("reservations.add_reservation", "Add reservations"),
        ("reservations.change_reservation", "Change reservations"),
        ("reservations.delete_reservation", "Remove reservations"),
    ],
    "Payments": [
        ("payments.view_payment", "View payments"),
        ("payments.add_payment", "Add payments"),
        ("payments.change_payment", "Change payments"),
        ("payments.delete_payment", "Remove payments"),
    ],
    "Customers": [
        ("customers.view_customer", "View customers"),
        ("customers.add_customer", "Add customers"),
        ("customers.change_customer", "Change customers"),
        ("customers.delete_customer", "Remove customers"),
    ],
    "Reports": [
        ("settings_app.view_reports", "View reports"),
    ],
}


class StaffAccountForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    password_confirm = forms.CharField(widget=forms.PasswordInput, min_length=8)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    position = forms.CharField(max_length=100)
    permissions = forms.MultipleChoiceField(
        choices=[
            option
            for options in PERMISSION_OPTIONS.values()
            for option in options
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already in use.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("password_confirm"):
            raise forms.ValidationError("The passwords do not match.")
        return cleaned_data

    def save(self, business):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
        )
        Employee.objects.create(
            business=business,
            user=user,
            first_name=data["first_name"],
            last_name=data["last_name"],
            position=data["position"],
            email=data["email"],
        )
        return user


class StaffPermissionForm(forms.Form):
    permissions = forms.MultipleChoiceField(
        choices=[
            option
            for options in PERMISSION_OPTIONS.values()
            for option in options
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )


    from django import forms

from .models import BusinessSettings


class GeneralSettingsForm(forms.ModelForm):
    class Meta:
        model = BusinessSettings

        fields = [
            "currency",
            "date_format",
            "time_format",
            "language",
        ]

        widgets = {
            "currency": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "MWK",
                    "maxlength": "10",
                }
            ),

            "date_format": forms.Select(
                choices=[
                    ("DD/MM/YYYY", "DD/MM/YYYY"),
                    ("MM/DD/YYYY", "MM/DD/YYYY"),
                    ("YYYY-MM-DD", "YYYY-MM-DD"),
                ],
                attrs={
                    "class": "form-select",
                },
            ),

            "time_format": forms.Select(
                attrs={
                    "class": "form-select",
                },
            ),

            "language": forms.Select(
                attrs={
                    "class": "form-select",
                },
            ),
        }


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = BusinessSettings

        fields = [
            "email_notifications",
            "low_stock_alerts",
            "sales_notifications",
            "payment_notifications",
            "report_notifications",
        ]

        widgets = {
            "email_notifications": forms.CheckboxInput(
                attrs={
                    "class": "notification-toggle",
                }
            ),

            "low_stock_alerts": forms.CheckboxInput(
                attrs={
                    "class": "notification-toggle",
                }
            ),

            "sales_notifications": forms.CheckboxInput(
                attrs={
                    "class": "notification-toggle",
                }
            ),

            "payment_notifications": forms.CheckboxInput(
                attrs={
                    "class": "notification-toggle",
                }
            ),

            "report_notifications": forms.CheckboxInput(
                attrs={
                    "class": "notification-toggle",
                }
            ),
        }