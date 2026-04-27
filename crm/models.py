from decimal import Decimal

from django.db import models
from django.urls import reverse


class Agent(models.Model):
    ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("Manager", "Manager"),
        ("Agent", "Agent"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="Agent")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Lead(models.Model):
    SOURCE_CHOICES = [
        ("Manual", "Manual"),
        ("Website", "Website"),
        ("Ads", "Ads"),
        ("Calls", "Calls"),
        ("Referral", "Referral"),
        ("Portal", "Portal"),
    ]
    STATUS_CHOICES = [
        ("New", "New"),
        ("Contacted", "Contacted"),
        ("Qualified", "Qualified"),
        ("Closed", "Closed"),
        ("Lost", "Lost"),
    ]

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default="Manual")
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    preferences = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="New")
    assigned_agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")
    next_follow_up = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("lead_list")


class Property(models.Model):
    TYPE_CHOICES = [
        ("Residential", "Residential"),
        ("Commercial", "Commercial"),
    ]
    AVAILABILITY_CHOICES = [
        ("Available", "Available"),
        ("Under Offer", "Under Offer"),
        ("Sold", "Sold"),
    ]

    title = models.CharField(max_length=160)
    property_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="Residential")
    location = models.CharField(max_length=160)
    price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    size = models.CharField(max_length=80, blank=True)
    amenities = models.TextField(blank=True)
    image = models.FileField(upload_to="properties/", blank=True)
    image_url = models.URLField(blank=True)
    availability = models.CharField(max_length=30, choices=AVAILABILITY_CHOICES, default="Available")
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="properties")
    map_query = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "properties"

    def __str__(self):
        return self.title

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url

    def get_absolute_url(self):
        return reverse("property_list")


class Client(models.Model):
    TYPE_CHOICES = [
        ("Buyer", "Buyer"),
        ("Seller", "Seller"),
    ]

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    client_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="Buyer")
    preferences = models.TextField(blank=True)
    linked_lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="clients")
    visited_properties = models.ManyToManyField(Property, blank=True, related_name="visitors")
    inquiries = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("client_list")


class Deal(models.Model):
    STAGE_CHOICES = [
        ("Inquiry", "Inquiry"),
        ("Negotiation", "Negotiation"),
        ("Agreement", "Agreement"),
        ("Closed", "Closed"),
    ]

    title = models.CharField(max_length=160)
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals")
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals")
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals")
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default="Inquiry")
    value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("2.00"))
    commission = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    expected_close = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.commission = (self.value * self.commission_rate) / Decimal("100")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("deal_list")


class Activity(models.Model):
    CHANNEL_CHOICES = [
        ("Call", "Call"),
        ("SMS", "SMS"),
        ("Email", "Email"),
        ("WhatsApp", "WhatsApp"),
        ("Meeting", "Meeting"),
    ]
    ENTITY_CHOICES = [
        ("lead", "Lead"),
        ("client", "Client"),
        ("deal", "Deal"),
    ]

    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES, default="lead")
    entity_id = models.PositiveIntegerField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="Call")
    direction = models.CharField(max_length=20, choices=[("Inbound", "Inbound"), ("Outbound", "Outbound")], default="Outbound")
    note = models.TextField()
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.channel} - {self.note[:40]}"


class Reminder(models.Model):
    title = models.CharField(max_length=160)
    entity_type = models.CharField(max_length=20, choices=Activity.ENTITY_CHOICES, default="lead")
    entity_id = models.PositiveIntegerField()
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="reminders")
    due_date = models.DateField()
    channel = models.CharField(max_length=20, choices=Activity.CHANNEL_CHOICES, default="Call")
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["completed", "due_date"]

    def __str__(self):
        return self.title


class DealDocument(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=160)
    file = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
