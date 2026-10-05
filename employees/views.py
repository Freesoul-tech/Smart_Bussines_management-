from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from businesses.models import Business
from core.access import business_permission_required, get_user_business

from .forms import EmployeeForm
from .models import Employee


@login_required
@business_permission_required("employees.view_employee")
def employee_list(request):

    business = get_user_business(request.user)

    employees = (
        Employee.objects.filter(
            business=business
        )
        if business
        else Employee.objects.none()
    )

    return render(
        request,
        "employees/employee_list.html",
        {
            "business": business,
            "employees": employees,
        },
    )


@login_required
@business_permission_required("employees.add_employee")
def employee_add(request):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    if request.method == "POST":

        form = EmployeeForm(request.POST)

        if form.is_valid():

            employee = form.save(commit=False)

            employee.business = business

            employee.save()

            return redirect("employee_list")

    else:

        form = EmployeeForm()

    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "business": business,
            "page_title": "Add Employee",
        },
    )


@login_required
@business_permission_required("employees.change_employee")
def employee_edit(request, employee_id):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    employee = get_object_or_404(
        Employee,
        id=employee_id,
        business=business,
    )

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            instance=employee,
        )

        if form.is_valid():

            form.save()

            return redirect("employee_list")

    else:

        form = EmployeeForm(
            instance=employee
        )

    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "business": business,
            "employee": employee,
            "page_title": "Edit Employee",
        },
    )


@login_required
@business_permission_required("employees.change_employee")
def employee_deactivate(request, employee_id):

    business = get_user_business(request.user)

    if not business:
        return redirect("business_setup")

    employee = get_object_or_404(
        Employee,
        id=employee_id,
        business=business,
    )

    if request.method == "POST":

        employee.employment_status = "inactive"

        employee.save()

    return redirect("employee_list")