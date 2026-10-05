from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect, render

from businesses.models import Business

from .forms import (
    GeneralSettingsForm,
    NotificationSettingsForm,
)
from .models import BusinessSettings
from .forms import PERMISSION_OPTIONS, StaffAccountForm, StaffPermissionForm
from core.access import get_user_business, is_business_owner, business_permission_required


User = get_user_model()


@login_required
def user_access(request):
    business = get_user_business(request.user)
    if not business or not is_business_owner(request.user, business):
        raise PermissionDenied

    employees = business.employees.select_related("user")
    if request.method == "POST":
        form = StaffAccountForm(request.POST)
        if form.is_valid():
            user = form.save(business)
            selected_permissions = form.cleaned_data["permissions"]
            permission_pairs = {
                permission
                for options in PERMISSION_OPTIONS.values()
                for permission, _ in options
                if permission in selected_permissions
            }
            user.user_permissions.set(
                Permission.objects.filter(
                    content_type__app_label__in={
                        permission.split(".")[0]
                        for permission in permission_pairs
                    },
                    codename__in={
                        permission.split(".")[1]
                        for permission in permission_pairs
                    },
                )
            )
            return redirect("settings_app:user_access")
    else:
        form = StaffAccountForm()

    return render(request, "settings_app/user_access.html", {
        "business": business,
        "employees": employees,
        "form": form,
        "active_page": "user_access",
        "permission_options": PERMISSION_OPTIONS,
    })


@login_required
def edit_user_permissions(request, employee_id):
    business = get_user_business(request.user)
    if not business or not is_business_owner(request.user, business):
        raise PermissionDenied

    employee = business.employees.select_related("user").filter(id=employee_id).first()
    if not employee or not employee.user:
        raise PermissionDenied

    allowed = {
        permission
        for options in PERMISSION_OPTIONS.values()
        for permission, _ in options
    }
    if request.method == "POST":
        form = StaffPermissionForm(request.POST)
        if form.is_valid():
            selected = set(form.cleaned_data["permissions"]) & allowed
            employee.user.user_permissions.set(
                Permission.objects.filter(
                    content_type__app_label__in={item.split(".")[0] for item in selected},
                    codename__in={item.split(".")[1] for item in selected},
                )
            )
            return redirect("settings_app:user_access")
    else:
        current = employee.user.user_permissions.all()
        current_values = {
            f"{permission.content_type.app_label}.{permission.codename}"
            for permission in current
            if f"{permission.content_type.app_label}.{permission.codename}" in allowed
        }
        form = StaffPermissionForm(initial={"permissions": current_values})

    return render(request, "settings_app/edit_user_permissions.html", {
        "business": business,
        "employee": employee,
        "form": form,
        "permission_options": PERMISSION_OPTIONS,
        "active_page": "user_access",
    })


@login_required
def remove_user(request, employee_id):
    business = get_user_business(request.user)
    if request.method != "POST" or not business or not is_business_owner(request.user, business):
        raise PermissionDenied

    employee = business.employees.select_related("user").filter(id=employee_id).first()
    if employee and employee.user_id != request.user.id:
        employee.user.delete()
    return redirect("settings_app:user_access")


ACCOMMODATION_MODELS = {
    "hotel",
    "motel",
    "lodge",
    "guest_house",
}


@login_required
@business_permission_required("settings_app.view_businesssettings")
def settings_view(request):

    business = get_user_business(request.user)

    if not business:
        return render(
            request,
            "settings_app/settings.html",
            {
                "business": None,
                "settings": None,
                "is_accommodation": False,
                "general_form": None,
                "notification_form": None,
            },
        )

    business_settings, _ = BusinessSettings.objects.get_or_create(
        business=business
    )

    if request.method == "POST":

        form_type = request.POST.get("form_type")

        # =========================================
        # GENERAL SETTINGS
        # =========================================

        if form_type == "general":

            general_form = GeneralSettingsForm(
                request.POST,
                instance=business_settings,
            )

            notification_form = NotificationSettingsForm(
                instance=business_settings
            )

            if general_form.is_valid():

                general_form.save()

                messages.success(
                    request,
                    "General settings saved successfully.",
                )

                return redirect("settings_app:settings")

        # =========================================
        # NOTIFICATIONS
        # =========================================

        elif form_type == "notifications":

            notification_form = NotificationSettingsForm(
                request.POST,
                instance=business_settings,
            )

            general_form = GeneralSettingsForm(
                instance=business_settings
            )

            if notification_form.is_valid():

                notification_form.save()

                messages.success(
                    request,
                    "Notification settings saved successfully.",
                )

                return redirect("settings_app:settings")

        else:

            general_form = GeneralSettingsForm(
                instance=business_settings
            )

            notification_form = NotificationSettingsForm(
                instance=business_settings
            )

    else:

        general_form = GeneralSettingsForm(
            instance=business_settings
        )

        notification_form = NotificationSettingsForm(
            instance=business_settings
        )

    is_accommodation = (
        business.business_model in ACCOMMODATION_MODELS
    )

    return render(
        request,
        "settings_app/settings.html",
        {
            "business": business,
            "settings": business_settings,
            "general_form": general_form,
            "notification_form": notification_form,
            "is_accommodation": is_accommodation,
        },
    )


@login_required
def toggle_theme(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method.",
            },
            status=405,
        )

    business = get_user_business(request.user)

    if not business:
        return JsonResponse(
            {
                "success": False,
                "message": "Business not found.",
            },
            status=404,
        )

    business_settings, _ = BusinessSettings.objects.get_or_create(
        business=business
    )

    theme = request.POST.get("theme")

    if theme not in {"system", "light", "dark"}:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid theme.",
            },
            status=400,
        )

    business_settings.theme = theme
    business_settings.save(
        update_fields=["theme", "updated_at"]
    )

    return JsonResponse(
        {
            "success": True,
            "theme": theme,
        }
    )