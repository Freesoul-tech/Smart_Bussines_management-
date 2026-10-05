from django.urls import path

from .views import (
    export_report_pdf,
    report_dashboard,
    report_pdf_preview,
)


urlpatterns = [
    path(
        "",
        report_dashboard,
        name="report_dashboard",
    ),

    path(
        "pdf-preview/",
        report_pdf_preview,
        name="report_pdf_preview",
    ),

    path(
        "export-pdf/",
        export_report_pdf,
        name="export_report_pdf",
    ),
]