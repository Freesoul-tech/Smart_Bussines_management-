from businesses.models import Business
from settings_app.models import BusinessSettings


def sbms_theme(request):
    theme = "light"

    if request.user.is_authenticated:
        business = Business.objects.filter(
            owner=request.user
        ).first()

        if business:
            settings = BusinessSettings.objects.filter(
                business=business
            ).first()

            if settings:
                theme = settings.theme

    return {
        "sbms_theme": theme,
    }