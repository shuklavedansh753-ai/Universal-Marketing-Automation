from django.db import models

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

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="notes"
    )

    note = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.lead.name}"