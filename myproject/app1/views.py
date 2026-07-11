from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import csv
from django.http import HttpResponse
from .models import Lead, Event, Note

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
                note=note_text
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

