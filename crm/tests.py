import json
from datetime import date
from decimal import Decimal

from django.test import Client as HttpClient
from django.test import TestCase
from django.urls import reverse

from .models import Agent, Deal, Lead, Property, Reminder


class CrmWorkflowTests(TestCase):
    def setUp(self):
        self.http = HttpClient()
        self.agent = Agent.objects.create(name="Test Agent", email="agent@example.com", role="Agent")

    def test_lead_save_button_creates_lead_and_reminder(self):
        response = self.http.post(reverse("lead_create"), {
            "name": "Save Button Lead",
            "phone": "12345678",
            "email": "save@example.com",
            "source": "Manual",
            "budget": "50000",
            "preferences": "Simple test preference",
            "status": "Qualified",
            "assigned_agent": self.agent.id,
            "next_follow_up": "2026-08-04",
        })
        self.assertRedirects(response, reverse("lead_list"))
        lead = Lead.objects.get(email="save@example.com")
        self.assertEqual(lead.status, "Qualified")
        self.assertTrue(Reminder.objects.filter(entity_type="lead", entity_id=lead.id).exists())

    def test_property_and_deal_workflow(self):
        lead = Lead.objects.create(name="Buyer", phone="111", assigned_agent=self.agent)
        prop = Property.objects.create(title="Test Flat", location="Delhi", price=Decimal("7000000"), agent=self.agent)
        response = self.http.post(reverse("deal_create"), {
            "title": "Buyer - Test Flat",
            "lead": lead.id,
            "client": "",
            "property": prop.id,
            "agent": self.agent.id,
            "stage": "Negotiation",
            "value": "7000000",
            "commission_rate": "2",
            "expected_close": date.today().isoformat(),
        })
        self.assertRedirects(response, reverse("deal_list"))
        deal = Deal.objects.get(title="Buyer - Test Flat")
        self.assertEqual(deal.commission, Decimal("140000"))

        self.http.post(reverse("deal_stage", args=[deal.id, "Closed"]))
        deal.refresh_from_db()
        self.assertEqual(deal.stage, "Closed")

    def test_api_capture_and_exports(self):
        response = self.http.post(reverse("api_lead_capture"), data=json.dumps({
            "name": "Webhook Lead",
            "phone": "999",
            "email": "webhook@example.com",
            "budget": 1200000,
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Lead.objects.filter(email="webhook@example.com").exists())

        csv_response = self.http.get(reverse("export_csv"))
        self.assertEqual(csv_response.status_code, 200)
        self.assertIn("Metric", csv_response.content.decode())

        pdf_response = self.http.get(reverse("export_pdf"))
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response["Content-Type"], "application/pdf")

    def test_role_blocks_property_create_for_agent(self):
        session = self.http.session
        session["role"] = "Agent"
        session.save()
        response = self.http.post(reverse("property_create"), {
            "title": "Blocked Property",
            "property_type": "Residential",
            "location": "Noida",
            "price": "5000000",
            "availability": "Available",
        })
        self.assertRedirects(response, reverse("property_list"))
        self.assertFalse(Property.objects.filter(title="Blocked Property").exists())

    def test_agent_can_be_added_and_deleted_by_admin(self):
        response = self.http.post(reverse("agent_create"), {
            "name": "New Agent",
            "email": "newagent@example.com",
            "phone": "1234567890",
            "role": "Agent",
            "active": "on",
        })
        self.assertRedirects(response, reverse("agent_list"))
        agent = Agent.objects.get(email="newagent@example.com")

        response = self.http.post(reverse("agent_delete", args=[agent.id]))
        self.assertRedirects(response, reverse("agent_list"))
        self.assertFalse(Agent.objects.filter(email="newagent@example.com").exists())
