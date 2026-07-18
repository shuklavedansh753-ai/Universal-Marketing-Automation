from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import csv
from django.http import HttpResponse
from .models import Lead, Event, Note, Campaign, CampaignRecipient
from .models import (
    Lead,
    Event,
    Note,
    Campaign,
    CampaignRecipient,
    EmailTemplate,
)
from django.utils import timezone
from django.contrib import messages
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings

def template_list(request):

    templates = EmailTemplate.objects.all().order_by("-id")

    return render(
        request,
        "app1/template_list.html",
        {
            "templates": templates
        }
    )

def create_lead(request):

    if request.method == "POST":
        Lead.objects.create(
            lead_type=request.POST.get("lead_type"),
            source="Website Widget",
            assigned_to=request.POST.get("assigned_to", ""),
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            mobile=request.POST.get("mobile"),
            company=request.POST.get("company"),
            message=request.POST.get("message"),
        )

        Event.objects.create(
            event_name="Lead Submitted"
        )
        return redirect("lead_list")

    return render(request, "app1/create_lead.html")




from django.db.models import Q
from django.core.paginator import Paginator

def lead_list(request):

    search = request.GET.get("search", "")
    status = request.GET.get("status", "")
    lead_type = request.GET.get("lead_type", "")

    # Show newest leads first
    leads = Lead.objects.all().order_by("-id")

    # Search
    if search:
        leads = leads.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(mobile__icontains=search) |
            Q(company__icontains=search)
        )

    # Filter by Status
    if status:
        leads = leads.filter(status=status)

    # Filter by Lead Type
    if lead_type:
        leads = leads.filter(lead_type=lead_type)

    # Dashboard Statistics
    total_leads = Lead.objects.count()
    new_leads = Lead.objects.filter(status="New").count()
    contacted_leads = Lead.objects.filter(status="Contacted").count()
    converted_leads = Lead.objects.filter(status="Converted").count()

    # Pagination
    paginator = Paginator(leads, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "app1/lead_list.html", {
        "leads": page_obj,
        "page_obj": page_obj,
        "search": search,
        "status": status,
        "lead_type": lead_type,
        "total_leads": total_leads,
        "new_leads": new_leads,
        "contacted_leads": contacted_leads,
        "converted_leads": converted_leads,
    })

def view_lead(request, id):

    lead = get_object_or_404(Lead, id=id)

    if request.method == "POST":

        note_text = request.POST.get("note")

        if note_text:
            Note.objects.create(
                lead=lead,
                note=note_text,
                note_type=request.POST.get("note_type", "follow_up")
            )

        return redirect("view_lead", id=id)

    return render(
        request,
        "app1/view_lead.html",
        {
            "lead": lead,
            "notes": lead.notes.all().order_by("-created_at")
        }
    )

def edit_lead(request, id):

    lead = get_object_or_404(Lead, id=id)

    if request.method == "POST":

        lead.lead_type = request.POST.get("lead_type")
        lead.source = request.POST.get("source")
        lead.status = request.POST.get("status")
        lead.assigned_to = request.POST.get("assigned_to")
        lead.name = request.POST.get("name")
        lead.email = request.POST.get("email")
        lead.mobile = request.POST.get("mobile")
        lead.company = request.POST.get("company")
        lead.message = request.POST.get("message")


        lead.save()

        return redirect("lead_list")

    return render(request, "app1/edit_lead.html", {"lead": lead})

def delete_lead(request, id):

    lead = get_object_or_404(Lead, id=id)

    lead.delete()

    return redirect("lead_list")

from .models import Event

def export_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leads.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'ID',
        'Lead Type',
        'Source',
        'Assigned To',
        'Status',
        'Name',
        'Email',
        'Mobile',
        'Company',
        'Message',
        'Created Date'
    ])

    leads = Lead.objects.all().order_by('-id')

    for lead in leads:
        writer.writerow([
            lead.id,
            lead.lead_type,
            lead.source,
            lead.assigned_to,
            lead.status,
            lead.name,
            lead.email,
            lead.mobile,
            lead.company,
            lead.message,
            lead.created_at.strftime("%d-%m-%Y %H:%M")
        ])
    return response

def track_event(request):

    if request.method == "POST":

        event_name = request.POST.get("event_name")

        Event.objects.create(
            event_name=event_name
        )

        return JsonResponse({"message": "Event Saved"})

    return JsonResponse({"error": "POST request required"})

from django.shortcuts import render, redirect
from .models import Campaign, EmailTemplate

def create_campaign(request):

    templates = EmailTemplate.objects.all()

    if request.method == "POST":

        # -----------------------------
        # Get Form Data
        # -----------------------------
        campaign_name = request.POST.get("campaign_name")
        campaign_type = request.POST.get("campaign_type")
        schedule_type = request.POST.get("schedule_type")
        schedule_date = request.POST.get("schedule_date")
        recurring_type = request.POST.get("recurring_type")
        template_id = request.POST.get("template")

        # -----------------------------
        # Validate Template
        # -----------------------------
        try:
            selected_template = EmailTemplate.objects.get(id=template_id)
        except EmailTemplate.DoesNotExist:
            messages.error(request, "Please select a valid email template.")
            return redirect("create_campaign")

        # -----------------------------
        # Validation 1
        # Scheduled Campaign requires Schedule Date
        # -----------------------------
        if schedule_type == "Scheduled" and not schedule_date:
            messages.error(request, "Please select a schedule date.")
            return redirect("create_campaign")

        # -----------------------------
        # Validation 2
        # Recurring Campaign requires Recurring Type
        # -----------------------------
        if schedule_type == "Recurring" and not recurring_type:
            messages.error(request, "Please select recurring type.")
            return redirect("create_campaign")

        # -----------------------------
        # Validation 3
        # Schedule Date cannot be in the past
        # -----------------------------
        if schedule_type == "Scheduled" and schedule_date:

            try:
                schedule_datetime = datetime.fromisoformat(schedule_date)
                schedule_datetime = timezone.make_aware(schedule_datetime)

                if schedule_datetime <= timezone.now():
                    messages.error(
                        request,
                        "Schedule date must be in the future."
                    )
                    return redirect("create_campaign")

            except ValueError:
                messages.error(request, "Invalid schedule date.")
                return redirect("create_campaign")

        # -----------------------------
        # Campaign Status
        # -----------------------------
        if schedule_type in ["Scheduled", "Recurring"]:
            status = "Scheduled"
        else:
            status = "Draft"

        # -----------------------------
        # Create Campaign
        # -----------------------------
        Campaign.objects.create(
            campaign_name=campaign_name,
            campaign_type=campaign_type,
            subject=selected_template.subject,
            template=selected_template.body,
            schedule_type=schedule_type,
            schedule_date=schedule_date or None,
            recurring_type=recurring_type or None,
            status=status,
        )

        messages.success(
            request,
            "Campaign created successfully."
        )

        return redirect("campaign_list")

    return render(
        request,
        "app1/create_campaign.html",
        {
            "templates": templates
        }
    )

from django.db.models import Count, Q

from django.db.models import Count

def campaign_list(request):

    search = request.GET.get("search", "")
    campaign_type = request.GET.get("campaign_type", "")
    status = request.GET.get("status", "")

    campaigns = Campaign.objects.all()

    if search:
        campaigns = campaigns.filter(
            campaign_name__icontains=search
        )

    if campaign_type:
        campaigns = campaigns.filter(
            campaign_type=campaign_type
        )

    if status:
        campaigns = campaigns.filter(
            status=status
        )

    campaigns = campaigns.annotate(
        audience_count=Count("campaignrecipient")
    ).order_by("-created_at")

    context = {
        "campaigns": campaigns,
        "search": search,
        "campaign_type": campaign_type,
        "status": status,

        # Dashboard Cards
        "total_campaigns": Campaign.objects.count(),
        "draft_campaigns": Campaign.objects.filter(status="Draft").count(),
        "scheduled_campaigns": Campaign.objects.filter(status="Scheduled").count(),
        "sent_campaigns": Campaign.objects.filter(status="Sent").count(),
    }

    return render(
        request,
        "app1/campaign_list.html",
        context,
    )

def edit_campaign(request, id):

    campaign = get_object_or_404(Campaign, id=id)

    if request.method == "POST":

        campaign.campaign_name = request.POST.get("campaign_name")

        campaign.campaign_type = request.POST.get("campaign_type")

        campaign.subject = request.POST.get("subject")

        campaign.template = request.POST.get("template")

        campaign.schedule_type = request.POST.get("schedule_type")

        campaign.schedule_date = request.POST.get("schedule_date") or None

        campaign.recurring_type = request.POST.get("recurring_type")

        campaign.save()

        return redirect("campaign_list")

    return render(
        request,
        "app1/edit_campaign.html",
        {
            "campaign": campaign
        }
    )

def delete_campaign(request, id):

    campaign = get_object_or_404(Campaign, id=id)

    campaign.delete()

    return redirect("campaign_list")

from django.shortcuts import get_object_or_404, redirect, render

from django.contrib import messages

def select_audience(request, campaign_id):

    campaign = get_object_or_404(Campaign, id=campaign_id)

    # -------------------------------
    # Filters
    # -------------------------------
    status = request.GET.get("status", "")
    lead_type = request.GET.get("lead_type", "")
    company = request.GET.get("company", "")
    assigned_to = request.GET.get("assigned_to", "")

    # New Filters
    source = request.GET.get("source", "")
    from_date = request.GET.get("from_date", "")
    to_date = request.GET.get("to_date", "")

    leads = Lead.objects.all()

    if status:
        leads = leads.filter(status=status)

    if lead_type:
        leads = leads.filter(lead_type=lead_type)

    if company:
        leads = leads.filter(company__icontains=company)

    if assigned_to:
        leads = leads.filter(
            assigned_to__icontains=assigned_to
        )

    # -------------------------------
    # New Advanced Filters
    # -------------------------------

    if source:
        leads = leads.filter(source=source)

    if from_date:
        leads = leads.filter(
            created_at__date__gte=from_date
        )

    if to_date:
        leads = leads.filter(
            created_at__date__lte=to_date
        )

    leads = leads.order_by("-id")

    # -------------------------------
    # Already Selected Audience
    # -------------------------------

    selected_ids = CampaignRecipient.objects.filter(
        campaign=campaign
    ).values_list(
        "lead_id",
        flat=True
    )

    # -------------------------------
    # Save Audience
    # -------------------------------

    if request.method == "POST":

        selected_leads = request.POST.getlist("lead_ids")

        if not selected_leads:

            messages.error(
                request,
                "Please select at least one lead."
            )

            return redirect(
                "select_audience",
                campaign_id=campaign.id
            )

        added = 0

        for lead_id in selected_leads:

            lead = get_object_or_404(
                Lead,
                id=lead_id
            )

            recipient, created = CampaignRecipient.objects.get_or_create(
                campaign=campaign,
                lead=lead
            )

            if created:
                added += 1

        messages.success(
            request,
            f"{added} recipient(s) added successfully."
        )

        return redirect("campaign_list")

    # -------------------------------
    # Page
    # -------------------------------

    return render(
        request,
        "app1/select_audience.html",
        {
            "campaign": campaign,
            "leads": leads,
            "selected_ids": selected_ids,

            "status": status,
            "lead_type": lead_type,
            "company": company,
            "assigned_to": assigned_to,

            # New Filters
            "source": source,
            "from_date": from_date,
            "to_date": to_date,
        },
    )

from django.contrib import messages

def send_campaign(request, id):

    campaign = get_object_or_404(Campaign, id=id)

    # Check audience
    recipients = CampaignRecipient.objects.filter(campaign=campaign)

    if not recipients.exists():
        messages.error(
            request,
            "Please select audience before sending."
        )
        return redirect("campaign_list")

    # Check scheduled campaign
    if (
        campaign.schedule_type == "Scheduled"
        and campaign.schedule_date
        and campaign.schedule_date > timezone.now()
    ):
        messages.warning(
            request,
            f"This campaign is scheduled for {campaign.schedule_date.strftime('%d %b %Y %I:%M %p')}."
        )
        return redirect("campaign_list")

    success_count = 0
    failed_count = 0

    # Send Campaign
    for recipient in recipients:

        lead = recipient.lead

        message = campaign.template

        first_name = lead.name.split()[0]

        last_name = ""

        if len(lead.name.split()) > 1:
            last_name = " ".join(lead.name.split()[1:])

        # Personalization
        message = message.replace("{{FirstName}}", first_name)
        message = message.replace("{{LastName}}", last_name)
        message = message.replace("{{Email}}", lead.email)
        message = message.replace("{{Mobile}}", lead.mobile)
        message = message.replace("{{Company}}", lead.company)

        try:

            send_mail(
                subject=campaign.subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lead.email],
                fail_silently=False,
            )

            recipient.sent_on = timezone.now()
            recipient.save()

            success_count += 1

        except Exception as e:

            print(f"Email failed for {lead.email}: {e}")

            failed_count += 1

    if success_count > 0:
        campaign.status = "Sent"
        campaign.save()

    if failed_count == 0:
        messages.success(
            request,
            f"Campaign sent successfully to {success_count} recipient(s)."
        )
    else:
        messages.warning(
            request,
            f"{success_count} email(s) sent successfully and {failed_count} failed."
        )

    return redirect("campaign_list")

def campaign_analytics(request, id):

    campaign = get_object_or_404(Campaign, id=id)

    recipients = CampaignRecipient.objects.filter(campaign=campaign)

    total = recipients.count()

    sent = recipients.filter(sent_on__isnull=False).count()

    opened = recipients.filter(opened_on__isnull=False).count()

    clicked = recipients.filter(clicked_on__isnull=False).count()

    open_rate = 0
    click_rate = 0

    if total > 0:
        open_rate = round((opened / total) * 100, 2)
        click_rate = round((clicked / total) * 100, 2)

    return render(
        request,
        "app1/campaign_analytics.html",
        {
            "campaign": campaign,
            "total": total,
            "sent": sent,
            "opened": opened,
            "clicked": clicked,
            "open_rate": open_rate,
            "click_rate": click_rate,
        },
    )

from django.utils import timezone

def mark_open(request, id):

    campaign = get_object_or_404(Campaign, id=id)

    recipients = CampaignRecipient.objects.filter(campaign=campaign)

    for recipient in recipients:
        recipient.opened_on = timezone.now()
        recipient.save()

    return redirect("campaign_analytics", id=id)


def mark_click(request, id):

    campaign = get_object_or_404(Campaign, id=id)

    recipients = CampaignRecipient.objects.filter(campaign=campaign)

    for recipient in recipients:
        recipient.clicked_on = timezone.now()
        recipient.save()

    return redirect("campaign_analytics", id=id)

def create_template(request):

    if request.method == "POST":

        EmailTemplate.objects.create(

            template_name=request.POST.get("template_name"),

            subject=request.POST.get("subject"),

            body=request.POST.get("body"),

        )

        return redirect("template_list")

    return render(request, "app1/create_template.html")

from django.shortcuts import render, redirect, get_object_or_404
from .models import EmailTemplate

def edit_template(request, id):

    template = get_object_or_404(EmailTemplate, id=id)

    if request.method == "POST":

        template.template_name = request.POST.get("template_name")
        template.subject = request.POST.get("subject")
        template.body = request.POST.get("body")

        template.save()

        return redirect("template_list")

    return render(
        request,
        "app1/edit_template.html",
        {
            "template": template
        }
    )

from django.shortcuts import get_object_or_404, redirect
from .models import EmailTemplate

def delete_template(request, id):

    template = get_object_or_404(EmailTemplate, id=id)

    template.delete()

    return redirect("template_list")

def preview_campaign(request, id):

    campaign = get_object_or_404(Campaign, id=id)

    recipient = CampaignRecipient.objects.filter(
        campaign=campaign
    ).select_related("lead").first()

    if recipient:

        lead = recipient.lead

        first_name = lead.name.split()[0]

        last_name = ""

        if len(lead.name.split()) > 1:
            last_name = " ".join(lead.name.split()[1:])

        preview = campaign.template

        preview = preview.replace(
            "{{FirstName}}",
            first_name
        )

        preview = preview.replace(
            "{{LastName}}",
            last_name
        )

        preview = preview.replace(
            "{{Email}}",
            lead.email
        )

        preview = preview.replace(
            "{{Mobile}}",
            lead.mobile
        )

        preview = preview.replace(
            "{{Company}}",
            lead.company
        )

    else:

        preview = campaign.template

    return render(

        request,

        "app1/preview_campaign.html",

        {

            "campaign": campaign,

            "preview": preview,

            "recipient": recipient,

        },

    )

def campaign_details(request, id):

    campaign = get_object_or_404(
        Campaign,
        id=id
    )

    recipients = CampaignRecipient.objects.filter(
        campaign=campaign
    ).select_related("lead")

    return render(
        request,
        "app1/campaign_details.html",
        {
            "campaign": campaign,
            "recipients": recipients,
        },
    )

def campaign_recipients(request, id):

    campaign = get_object_or_404(
        Campaign,
        id=id
    )

    recipients = CampaignRecipient.objects.filter(
        campaign=campaign
    ).select_related("lead")

    return render(
        request,
        "app1/campaign_recipients.html",
        {
            "campaign": campaign,
            "recipients": recipients,
        },
    )