from django.urls import path

from .views import activity_add, activity_list, dashboard, package_add, package_list

app_name = "lodge"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("activities/", activity_list, name="activities"),
    path("activities/add/", activity_add, name="activity_add"),
    path("packages/", package_list, name="packages"),
    path("packages/add/", package_add, name="package_add"),
]
