from django import forms

from .models import Activity, Agent, Client, Deal, DealDocument, Lead, Property, Reminder


class DateInput(forms.DateInput):
    input_type = "date"


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ["name", "email", "phone", "role", "active"]


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["name", "phone", "email", "source", "budget", "preferences", "status", "assigned_agent", "next_follow_up"]
        widgets = {"next_follow_up": DateInput(), "preferences": forms.Textarea(attrs={"rows": 3})}


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ["title", "property_type", "location", "price", "size", "amenities", "image", "image_url", "availability", "agent", "map_query"]
        widgets = {"amenities": forms.Textarea(attrs={"rows": 3})}


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "phone", "email", "client_type", "preferences", "linked_lead", "visited_properties", "inquiries"]
        widgets = {
            "preferences": forms.Textarea(attrs={"rows": 3}),
            "inquiries": forms.Textarea(attrs={"rows": 3}),
            "visited_properties": forms.CheckboxSelectMultiple(),
        }


class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ["title", "lead", "client", "property", "agent", "stage", "value", "commission_rate", "expected_close"]
        widgets = {"expected_close": DateInput()}


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["entity_type", "entity_id", "channel", "direction", "note", "agent", "due_date", "completed"]
        widgets = {"due_date": DateInput(), "note": forms.Textarea(attrs={"rows": 3})}


class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ["title", "entity_type", "entity_id", "agent", "due_date", "channel", "completed"]
        widgets = {"due_date": DateInput()}


class DealDocumentForm(forms.ModelForm):
    class Meta:
        model = DealDocument
        fields = ["title", "file"]
