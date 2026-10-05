from businesses.models import Business
from django.core.exceptions import PermissionDenied
from functools import wraps


def get_user_business(user):
    """Return the business owned by or employing the authenticated user."""
    if not user or not user.is_authenticated:
        return None

    business = Business.objects.filter(owner=user).first()
    if business:
        return business

    employee = (
        user.employee_profiles
        .filter(employment_status="active")
        .select_related("business")
        .first()
    )
    return employee.business if employee else None


def is_business_owner(user, business=None):
    business = business or get_user_business(user)
    return bool(business and business.owner_id == user.id)


def business_permission_required(permission):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            business = get_user_business(request.user)
            if not business or not (
                is_business_owner(request.user, business)
                or request.user.has_perm(permission)
            ):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapped
    return decorator