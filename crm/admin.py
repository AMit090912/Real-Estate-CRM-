from django.contrib import admin

from .models import Activity, Agent, Client, Deal, DealDocument, Lead, Property, Reminder


admin.site.register(Agent)
admin.site.register(Lead)
admin.site.register(Property)
admin.site.register(Client)
admin.site.register(Deal)
admin.site.register(Activity)
admin.site.register(Reminder)
admin.site.register(DealDocument)
