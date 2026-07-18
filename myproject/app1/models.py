from django.db import models
from django.utils import timezone
class Lead(models.Model):

    LEAD_TYPES = [
        ("Contact Us", "Contact Us"),
        ("Enquire Now", "Enquire Now"),
        ("Request Demo", "Request Demo"),
    ]

    STATUS_CHOICES = [
        ("New", "New"),
        ("Contacted", "Contacted"),
        ("Qualified", "Qualified"),
        ("Interested", "Interested"),
        ("Converted", "Converted"),
        ("Lost", "Lost"),
    ]

    lead_type = models.CharField(
        max_length=30,
        choices=LEAD_TYPES,
        default="Contact Us"
    )
    source = models.CharField(
        max_length=50,
        default="Website Widget"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="New"
    )
    assigned_to = models.CharField(
        max_length=100,
        blank=True
    )

    name = models.CharField(max_length=100)

    email = models.EmailField()

    mobile = models.CharField(max_length=15)

    company = models.CharField(max_length=100)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Event(models.Model):

    event_name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_name

class Note(models.Model):

    FOLLOW_UP = "follow_up"
    CALL_REMARK = "call_remark"
    MEETING_REMARK = "meeting_remark"

    NOTE_TYPES = [
        (FOLLOW_UP, "Follow-up"),
        (CALL_REMARK, "Call Remark"),
        (MEETING_REMARK, "Meeting Remark"),
    ]

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="notes"
    )

    note_type = models.CharField(
        max_length=20,
        choices=NOTE_TYPES,
        default=FOLLOW_UP
    )

    note = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_note_type_display()} - {self.lead.name}"

class Campaign(models.Model):

    CAMPAIGN_TYPES = [
        ("Email", "Email"),
        ("SMS", "SMS"),
        ("WhatsApp", "WhatsApp"),
        ("Push", "Push"),
    ]

    SCHEDULE_TYPES = [
        ("Immediate", "Immediate"),
        ("Scheduled", "Scheduled"),
        ("Recurring", "Recurring"),
    ]

    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Scheduled", "Scheduled"),
        ("Sent", "Sent"),
    ]

    campaign_name = models.CharField(max_length=150)

    campaign_type = models.CharField(
        max_length=20,
        choices=CAMPAIGN_TYPES
    )

    subject = models.CharField(max_length=255)

    template = models.TextField()

    schedule_type = models.CharField(
        max_length=20,
        choices=SCHEDULE_TYPES,
        default="Immediate"
    )

    schedule_date = models.DateTimeField(
        null=True,
        blank=True
    )

    recurring_type = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Draft"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.campaign_name

class CampaignRecipient(models.Model):

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE
    )

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE
    )

    sent_on = models.DateTimeField(
        blank=True,
        null=True
    )

    opened_on = models.DateTimeField(
        blank=True,
        null=True
    )

    clicked_on = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.campaign} - {self.lead}"



class EmailTemplate(models.Model):

    template_name = models.CharField(max_length=100)

    subject = models.CharField(max_length=200)

    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.template_name