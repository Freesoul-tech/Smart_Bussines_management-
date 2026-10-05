from django.urls import path

from . import views


app_name = "settings_app"


urlpatterns = [
    path(
        "",
        views.settings_view,
        name="settings",
    ),

    path(
        "toggle-theme/",
        views.toggle_theme,
        name="toggle_theme",
    ),
    path(
        "users/",
        views.user_access,
        name="user_access",
    ),
    path(
        "users/<int:employee_id>/remove/",
        views.remove_user,
        name="remove_user",
    ),
    path(
        "users/<int:employee_id>/permissions/",
        views.edit_user_permissions,
        name="edit_user_permissions",
    ),
]
