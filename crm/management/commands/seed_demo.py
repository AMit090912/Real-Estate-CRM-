from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from crm.models import Activity, Agent, Client, Deal, Lead, Property, Reminder


class Command(BaseCommand):
    help = "Seed demo data for the real estate CRM assignment."

    def handle(self, *args, **options):
        Activity.objects.all().delete()
        Reminder.objects.all().delete()
        Deal.objects.all().delete()
        Client.objects.all().delete()
        Lead.objects.all().delete()
        Property.objects.all().delete()
        Agent.objects.all().delete()

        admin = Agent.objects.create(name="Aarav Sharma", email="admin@estatecrm.local", phone="+91 90000 10001", role="Admin")
        manager = Agent.objects.create(name="Meera Iyer", email="manager@estatecrm.local", phone="+91 90000 10002", role="Manager")
        nisha = Agent.objects.create(name="Nisha Rao", email="nisha@estatecrm.local", phone="+91 90000 10003", role="Agent")
        kabir = Agent.objects.create(name="Kabir Khan", email="kabir@estatecrm.local", phone="+91 90000 10004", role="Agent")

        lead1 = Lead.objects.create(
            name="Rohan Malhotra",
            phone="+91 98765 43210",
            email="rohan@example.com",
            source="Website",
            budget=Decimal("12500000"),
            preferences="3 BHK near metro, balcony and parking",
            status="Qualified",
            assigned_agent=nisha,
            next_follow_up=date.today() + timedelta(days=1),
        )
        lead2 = Lead.objects.create(
            name="Priya Menon",
            phone="+91 90000 11223",
            email="priya@example.com",
            source="Referral",
            budget=Decimal("7800000"),
            preferences="Ready-to-move 2 BHK near school",
            status="Contacted",
            assigned_agent=kabir,
            next_follow_up=date.today(),
        )
        lead3 = Lead.objects.create(
            name="Sanjay Kapoor",
            phone="+91 95555 33110",
            email="sanjay@example.com",
            source="Ads",
            budget=Decimal("30000000"),
            preferences="Commercial office with road frontage",
            status="New",
            assigned_agent=nisha,
            next_follow_up=date.today() + timedelta(days=2),
        )

        prop1 = Property.objects.create(
            title="Skyline Residences 3 BHK",
            property_type="Residential",
            location="Whitefield, Bengaluru",
            price=Decimal("11800000"),
            size="1680 sq ft",
            amenities="Pool, gym, clubhouse, covered parking",
            image_url="https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=900&q=80",
            availability="Available",
            agent=nisha,
            map_query="Whitefield Bengaluru",
        )
        Property.objects.create(
            title="Central Park 2 BHK",
            property_type="Residential",
            location="Baner, Pune",
            price=Decimal("7600000"),
            size="1120 sq ft",
            amenities="Garden, power backup, security",
            image_url="https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=900&q=80",
            availability="Available",
            agent=kabir,
            map_query="Baner Pune",
        )
        prop3 = Property.objects.create(
            title="Prime High Street Office",
            property_type="Commercial",
            location="Andheri East, Mumbai",
            price=Decimal("28500000"),
            size="2100 sq ft",
            amenities="Lift, pantry, basement parking, reception",
            image_url="https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=80",
            availability="Under Offer",
            agent=nisha,
            map_query="Andheri East Mumbai",
        )

        client1 = Client.objects.create(
            name="Rohan Malhotra",
            phone="+91 98765 43210",
            email="rohan@example.com",
            client_type="Buyer",
            preferences="Premium 3 BHK in Bengaluru",
            linked_lead=lead1,
            inquiries="Asked for floor plan and possession date",
        )
        client1.visited_properties.add(prop1)

        deal1 = Deal.objects.create(
            title="Rohan - Skyline Residences",
            lead=lead1,
            client=client1,
            property=prop1,
            agent=nisha,
            stage="Negotiation",
            value=Decimal("11800000"),
            commission_rate=Decimal("2.00"),
            expected_close=date.today() + timedelta(days=18),
        )
        Deal.objects.create(
            title="Sanjay - Prime Office",
            lead=lead3,
            property=prop3,
            agent=nisha,
            stage="Inquiry",
            value=Decimal("28500000"),
            commission_rate=Decimal("1.50"),
            expected_close=date.today() + timedelta(days=30),
        )

        Activity.objects.create(entity_type="lead", entity_id=lead1.id, channel="Call", direction="Outbound", note="Explained project pricing and scheduled site visit.", agent=nisha, completed=True)
        Activity.objects.create(entity_type="lead", entity_id=lead2.id, channel="SMS", direction="Outbound", note="Shared shortlist and asked for visit availability.", agent=kabir, due_date=date.today())
        Reminder.objects.create(title="Follow up with Priya", entity_type="lead", entity_id=lead2.id, agent=kabir, due_date=date.today(), channel="Call")
        Reminder.objects.create(title="Send updated agreement", entity_type="deal", entity_id=deal1.id, agent=nisha, due_date=date.today() + timedelta(days=1), channel="Email")

        self.stdout.write(self.style.SUCCESS(f"Seeded CRM demo data for {admin.name}, {manager.name}, {nisha.name}, and {kabir.name}."))
