from django.urls import path
from . import views

urlpatterns = [

    path("create/", views.create_lead, name="create_lead"),

    path("", views.lead_list, name="lead_list"),

    path("track/", views.track_event, name="track_event"),

    path("view/<int:id>/", views.view_lead, name="view_lead"),

    path("edit/<int:id>/", views.edit_lead, name="edit_lead"),

    path("delete/<int:id>/", views.delete_lead, name="delete_lead"),

    path("export/", views.export_csv, name="export_csv"),

]