from django.contrib import admin
from .models import Lead, Event
from .models import Campaign, CampaignRecipient

admin.site.register(Lead)
admin.site.register(Event)
admin.site.register(Campaign)
admin.site.register(CampaignRecipient)