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
        ("Converted", "Converted"),
        ("Lost", "Lost"),
    ]

    lead_type = models.CharField(
        max_length=30,
        choices=LEAD_TYPES,
        default="Contact Us"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="New"
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