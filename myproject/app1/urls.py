from django.urls import path
from . import views
from .models import Lead, Event, Note, Campaign, CampaignRecipient

urlpatterns = [

    path("create/", views.create_lead, name="create_lead"),

    path("", views.lead_list, name="lead_list"),

    path("track/", views.track_event, name="track_event"),

    path("view/<int:id>/", views.view_lead, name="view_lead"),

    path("edit/<int:id>/", views.edit_lead, name="edit_lead"),

    path("delete/<int:id>/", views.delete_lead, name="delete_lead"),

    path("export/", views.export_csv, name="export_csv"),

    path("leads/", views.lead_list, name="lead_list"),
    path("lead/<int:id>/", views.view_lead, name="view_lead"),
    path("edit/<int:id>/", views.edit_lead, name="edit_lead"),
    path("delete/<int:id>/", views.delete_lead, name="delete_lead"),
    path("export/", views.export_csv, name="export_csv"),
    path("track/", views.track_event, name="track_event"),

    # Module 3
    path("campaigns/", views.campaign_list, name="campaign_list"),
    path("campaigns/create/", views.create_campaign, name="create_campaign"),
    path("campaigns/edit/<int:id>/", views.edit_campaign, name="edit_campaign"),
    path("campaigns/delete/<int:id>/", views.delete_campaign, name="delete_campaign"),
path(
    "campaigns/<int:campaign_id>/audience/",
    views.select_audience,
    name="select_audience",
),
path(
        "campaigns/send/<int:id>/",
        views.send_campaign,
        name="send_campaign",
    ),
path(
    "campaigns/send/<int:id>/",
    views.send_campaign,
    name="send_campaign",
),
path(
    "campaigns/analytics/<int:id>/",
    views.campaign_analytics,
    name="campaign_analytics",
),
path(
    "campaigns/open/<int:id>/",
    views.mark_open,
    name="mark_open",
),

path(
    "campaigns/click/<int:id>/",
    views.mark_click,
    name="mark_click",
),
path(
    "templates/",
    views.template_list,
    name="template_list",
),

path(
    "templates/create/",
    views.create_template,
    name="create_template",
),
path(
    "templates/edit/<int:id>/",
    views.edit_template,
    name="edit_template",
),
path(
    "templates/delete/<int:id>/",
    views.delete_template,
    name="delete_template",
),
path(
    "campaigns/preview/<int:id>/",
    views.preview_campaign,
    name="preview_campaign",
),
path(
    "campaigns/details/<int:id>/",
    views.campaign_details,
    name="campaign_details",
),
path(
    "campaigns/recipients/<int:id>/",
    views.campaign_recipients,
    name="campaign_recipients",
),
]