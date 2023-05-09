from django.urls import path
from nautobot.extras.views import ObjectNotesView

from . import views
from .models import CPU

urlpatterns = [
    path("cpus/", views.CPUListView.as_view(), name="cpu_list"),
    path("cpus/add", views.CPUEditView.as_view(), name="cpu_add"),
    path("cpus/edit/", views.CPUBulkEditView.as_view(), name="cpu_bulk_edit"),
    path("cpus/import/", views.CPUBulkImportView.as_view(), name="cpu_import"),
    path("cpus/delete/", views.CPUBulkDeleteView.as_view(), name="cpu_bulk_delete"),
    path("cpus/<slug:slug>/", views.CPUView.as_view(), name="cpu"),
    path("cpus/<slug:slug>/edit", views.CPUEditView.as_view(), name="cpu_edit"),
    path("cpus/<slug:slug>/changelog/", views.CPUChangeLogView.as_view(), name="cpu_changelog", kwargs={"model": CPU}),
    path("cpus/<slug:slug>/delete/", views.CPUDeleteView.as_view(), name="cpu_delete"),
    path("cpus/<slug:slug>/notes/", ObjectNotesView.as_view(), name="cpu_notes", kwargs={"model": CPU}),
]
