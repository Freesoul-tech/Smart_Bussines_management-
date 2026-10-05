from django.contrib import admin
from django.urls import include, path


urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include('accounts.urls')),

    path('business/', include('businesses.urls')),

    path('dashboard/', include('dashboard.urls')),

    path('employees/', include('employees.urls')),
    
    path("rooms/", include("rooms.urls")),

    path("reservations/", include("reservations.urls")),

    path("motel/", include("motel.urls")),

    path("lodge/", include("lodge.urls")),

    path("bakery/", include("bakery.urls")),

    path("pub-bar/", include("pub_bar.urls")),

    path("boutique/", include("boutique.urls")),

    path("payments/", include("payments.urls")),
    
    path("customers/", include("customers.urls")),
    
    path("reports/", include("reports.urls")),
    
    path("settings/", include("settings_app.urls")),

]