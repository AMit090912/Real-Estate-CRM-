import csv
import json
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import ActivityForm, AgentForm, ClientForm, DealDocumentForm, DealForm, LeadForm, PropertyForm, ReminderForm
from .models import Activity, Agent, Client, Deal, DealDocument, Lead, Property, Reminder


def role_allowed(request, roles):
    return request.session.get("role", "Admin") in roles


def require_role(request, roles):
    if role_allowed(request, roles):
        return True
    messages.error(request, "Your selected role does not have permission for that action.")
    return False


def get_lightest_agent():
    agents = Agent.objects.filter(role="Agent", active=True).annotate(open_leads=Count("leads")).order_by("open_leads", "name")
    return agents.first()


def set_role(request):
    if request.method == "POST":
        request.session["role"] = request.POST.get("role", "Admin")
        messages.success(request, f"Role changed to {request.session['role']}.")
    return redirect(request.META.get("HTTP_REFERER") or "dashboard")


def dashboard(request):
    context = {
        "stats": get_report_stats(),
        "notifications": get_notifications()[:8],
        "recent_leads": Lead.objects.select_related("assigned_agent")[:5],
        "recent_deals": Deal.objects.select_related("agent", "property")[:5],
    }
    return render(request, "crm/dashboard.html", context)


def lead_list(request):
    leads = Lead.objects.select_related("assigned_agent")
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if query:
        leads = leads.filter(name__icontains=query) | leads.filter(phone__icontains=query) | leads.filter(email__icontains=query) | leads.filter(preferences__icontains=query)
    if status:
        leads = leads.filter(status=status)
    return render(request, "crm/lead_list.html", {"leads": leads, "status_choices": Lead.STATUS_CHOICES, "query": query, "status": status})


def lead_create(request):
    if not require_role(request, ["Admin", "Manager", "Agent"]):
        return redirect("lead_list")
    form = LeadForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        lead = form.save(commit=False)
        if not lead.assigned_agent:
            lead.assigned_agent = get_lightest_agent()
        lead.save()
        Reminder.objects.create(title=f"First contact: {lead.name}", entity_type="lead", entity_id=lead.id, agent=lead.assigned_agent, due_date=date.today() + timedelta(days=1), channel="Call")
        messages.success(request, "Lead saved successfully.")
        return redirect("lead_list")
    return render(request, "crm/form.html", {"title": "Add Lead", "form": form, "back_url": reverse("lead_list")})


def lead_update(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if not require_role(request, ["Admin", "Manager", "Agent"]):
        return redirect("lead_list")
    form = LeadForm(request.POST or None, instance=lead)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Lead updated.")
        return redirect("lead_list")
    return render(request, "crm/form.html", {"title": "Edit Lead", "form": form, "back_url": reverse("lead_list")})


@require_POST
def lead_progress(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    statuses = [choice[0] for choice in Lead.STATUS_CHOICES]
    current = statuses.index(lead.status)
    lead.status = statuses[min(current + 1, len(statuses) - 1)]
    lead.save(update_fields=["status"])
    messages.success(request, f"Lead moved to {lead.status}.")
    return redirect("lead_list")


@require_POST
def lead_delete(request, pk):
    if require_role(request, ["Admin"]):
        get_object_or_404(Lead, pk=pk).delete()
        messages.success(request, "Lead deleted.")
    return redirect("lead_list")


def property_list(request):
    properties = Property.objects.select_related("agent")
    query = request.GET.get("q", "").strip()
    property_type = request.GET.get("type", "")
    availability = request.GET.get("availability", "")
    if query:
        properties = properties.filter(title__icontains=query) | properties.filter(location__icontains=query) | properties.filter(amenities__icontains=query)
    if property_type:
        properties = properties.filter(property_type=property_type)
    if availability:
        properties = properties.filter(availability=availability)
    return render(request, "crm/property_list.html", {"properties": properties, "query": query, "property_type": property_type, "availability": availability})


def property_create(request):
    if not require_role(request, ["Admin", "Manager"]):
        return redirect("property_list")
    form = PropertyForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Property saved.")
        return redirect("property_list")
    return render(request, "crm/form.html", {"title": "Add Property", "form": form, "back_url": reverse("property_list"), "multipart": True})


def property_update(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if not require_role(request, ["Admin", "Manager"]):
        return redirect("property_list")
    form = PropertyForm(request.POST or None, request.FILES or None, instance=prop)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Property updated.")
        return redirect("property_list")
    return render(request, "crm/form.html", {"title": "Edit Property", "form": form, "back_url": reverse("property_list"), "multipart": True})


@require_POST
def property_delete(request, pk):
    if require_role(request, ["Admin"]):
        get_object_or_404(Property, pk=pk).delete()
        messages.success(request, "Property deleted.")
    return redirect("property_list")


def client_list(request):
    return render(request, "crm/client_list.html", {"clients": Client.objects.prefetch_related("visited_properties").select_related("linked_lead")})


def client_create(request):
    if not require_role(request, ["Admin", "Manager", "Agent"]):
        return redirect("client_list")
    form = ClientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Client saved.")
        return redirect("client_list")
    return render(request, "crm/form.html", {"title": "Add Client", "form": form, "back_url": reverse("client_list")})


def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=client)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Client updated.")
        return redirect("client_list")
    return render(request, "crm/form.html", {"title": "Edit Client", "form": form, "back_url": reverse("client_list")})


@require_POST
def client_delete(request, pk):
    if require_role(request, ["Admin"]):
        get_object_or_404(Client, pk=pk).delete()
        messages.success(request, "Client deleted.")
    return redirect("client_list")


def deal_list(request):
    stages = [choice[0] for choice in Deal.STAGE_CHOICES]
    lanes = [{"stage": stage, "deals": Deal.objects.filter(stage=stage).select_related("client", "property", "agent")} for stage in stages]
    return render(request, "crm/deal_list.html", {"stages": stages, "lanes": lanes})


def deal_create(request):
    form = DealForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Deal saved.")
        return redirect("deal_list")
    return render(request, "crm/form.html", {"title": "Add Deal", "form": form, "back_url": reverse("deal_list")})


def deal_update(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    form = DealForm(request.POST or None, instance=deal)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Deal updated.")
        return redirect("deal_list")
    doc_form = DealDocumentForm()
    return render(request, "crm/deal_form.html", {"title": "Edit Deal", "form": form, "doc_form": doc_form, "deal": deal})


@require_POST
def deal_stage(request, pk, stage):
    deal = get_object_or_404(Deal, pk=pk)
    valid = [choice[0] for choice in Deal.STAGE_CHOICES]
    if stage in valid:
        deal.stage = stage
        if stage == "Closed":
            deal.closed_at = date.today()
        deal.save()
        messages.success(request, f"Deal moved to {stage}.")
    return redirect("deal_list")


@require_POST
def deal_delete(request, pk):
    if require_role(request, ["Admin"]):
        get_object_or_404(Deal, pk=pk).delete()
        messages.success(request, "Deal deleted.")
    return redirect("deal_list")


@require_POST
def document_upload(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    form = DealDocumentForm(request.POST, request.FILES)
    if form.is_valid():
        doc = form.save(commit=False)
        doc.deal = deal
        doc.save()
        messages.success(request, "Document uploaded.")
    else:
        messages.error(request, "Please choose a document before uploading.")
    return redirect("deal_update", pk=pk)


def communications(request):
    activity_form = ActivityForm(prefix="activity")
    reminder_form = ReminderForm(prefix="reminder")
    return render(request, "crm/communications.html", {"activities": Activity.objects.select_related("agent"), "reminders": Reminder.objects.select_related("agent"), "activity_form": activity_form, "reminder_form": reminder_form})


@require_POST
def activity_create(request):
    form = ActivityForm(request.POST, prefix="activity")
    if form.is_valid():
        form.save()
        messages.success(request, "Activity logged.")
    else:
        messages.error(request, "Activity could not be saved. Check the form fields.")
    return redirect("communications")


@require_POST
def reminder_create(request):
    form = ReminderForm(request.POST, prefix="reminder")
    if form.is_valid():
        form.save()
        messages.success(request, "Reminder saved.")
    else:
        messages.error(request, "Reminder could not be saved. Check the form fields.")
    return redirect("communications")


@require_POST
def reminder_toggle(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk)
    reminder.completed = not reminder.completed
    reminder.save(update_fields=["completed"])
    return redirect("communications")


def agent_list(request):
    agents = Agent.objects.all().annotate(lead_count=Count("leads"), deal_count=Count("deals"))
    return render(request, "crm/agent_list.html", {"agents": agents})


def agent_create(request):
    if not require_role(request, ["Admin", "Manager"]):
        return redirect("agent_list")
    form = AgentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Agent saved.")
        return redirect("agent_list")
    return render(request, "crm/form.html", {"title": "Add Agent", "form": form, "back_url": reverse("agent_list")})


def agent_update(request, pk):
    agent = get_object_or_404(Agent, pk=pk)
    if not require_role(request, ["Admin", "Manager"]):
        return redirect("agent_list")
    form = AgentForm(request.POST or None, instance=agent)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Agent updated.")
        return redirect("agent_list")
    return render(request, "crm/form.html", {"title": "Edit Agent", "form": form, "back_url": reverse("agent_list")})


@require_POST
def agent_delete(request, pk):
    if require_role(request, ["Admin"]):
        get_object_or_404(Agent, pk=pk).delete()
        messages.success(request, "Agent deleted.")
    return redirect("agent_list")


def reports(request):
    return render(request, "crm/reports.html", {"stats": get_report_stats(), "lead_status": lead_status_rows(), "agent_rows": agent_report_rows()})


def integrations(request):
    form = LeadForm(initial={"source": "Website", "status": "New"})
    return render(request, "crm/integrations.html", {"form": form})


@require_POST
def website_capture(request):
    form = LeadForm(request.POST)
    if form.is_valid():
        lead = form.save(commit=False)
        lead.source = "Website"
        lead.status = "New"
        if not lead.assigned_agent:
            lead.assigned_agent = get_lightest_agent()
        lead.save()
        Reminder.objects.create(title=f"First contact: {lead.name}", entity_type="lead", entity_id=lead.id, agent=lead.assigned_agent, due_date=date.today() + timedelta(days=1), channel="Call")
        messages.success(request, "Website lead captured and assigned.")
        return redirect("lead_list")
    messages.error(request, "Lead capture failed. Please check the fields.")
    return redirect("integrations")


@csrf_exempt
def api_lead_capture(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    data = json.loads(request.body or "{}")
    lead = Lead.objects.create(
        name=data.get("name", "Unnamed Lead"),
        phone=data.get("phone", ""),
        email=data.get("email", ""),
        source=data.get("source", "Portal"),
        budget=Decimal(str(data.get("budget") or 0)),
        preferences=data.get("preferences", ""),
        status="New",
        assigned_agent=get_lightest_agent(),
        next_follow_up=date.today() + timedelta(days=1),
    )
    Reminder.objects.create(title=f"First contact: {lead.name}", entity_type="lead", entity_id=lead.id, agent=lead.assigned_agent, due_date=date.today() + timedelta(days=1), channel="Call")
    return JsonResponse({"id": lead.id, "name": lead.name, "assigned_agent": lead.assigned_agent.name if lead.assigned_agent else ""}, status=201)


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="crm-report.csv"'
    writer = csv.writer(response)
    stats = get_report_stats()
    writer.writerow(["Metric", "Value"])
    for key, value in stats.items():
        writer.writerow([key.replace("_", " ").title(), value])
    writer.writerow([])
    writer.writerow(["Agent", "Leads", "Deals", "Pipeline", "Commission"])
    for row in agent_report_rows():
        writer.writerow([row["agent"].name, row["leads"], row["deals"], row["pipeline"], row["commission"]])
    return response


def export_pdf(request):
    stats = get_report_stats()
    lines = [
        "Real Estate CRM Report",
        f"Leads: {stats['total_leads']}",
        f"Properties: {stats['total_properties']}",
        f"Active Deals: {stats['active_deals']}",
        f"Pipeline: INR {stats['pipeline']}",
        f"Revenue: INR {stats['revenue']}",
    ]
    response = HttpResponse(minimal_pdf(lines), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="crm-report.pdf"'
    return response


def get_report_stats():
    closed = Deal.objects.filter(stage="Closed")
    total_leads = Lead.objects.count()
    converted = Lead.objects.filter(status__in=["Qualified", "Closed"]).count()
    return {
        "total_leads": total_leads,
        "total_properties": Property.objects.count(),
        "active_deals": Deal.objects.exclude(stage="Closed").count(),
        "pipeline": Deal.objects.aggregate(total=Sum("value"))["total"] or Decimal("0"),
        "revenue": closed.aggregate(total=Sum("value"))["total"] or Decimal("0"),
        "commission": Deal.objects.aggregate(total=Sum("commission"))["total"] or Decimal("0"),
        "conversion_rate": round((converted / total_leads) * 100) if total_leads else 0,
        "pending_followups": Reminder.objects.filter(completed=False).count(),
    }


def lead_status_rows():
    return [{"status": status, "count": Lead.objects.filter(status=status).count()} for status, _ in Lead.STATUS_CHOICES]


def agent_report_rows():
    rows = []
    for agent in Agent.objects.filter(role="Agent"):
        deals = Deal.objects.filter(agent=agent)
        rows.append({
            "agent": agent,
            "leads": Lead.objects.filter(assigned_agent=agent).count(),
            "deals": deals.count(),
            "pipeline": deals.aggregate(total=Sum("value"))["total"] or Decimal("0"),
            "commission": deals.aggregate(total=Sum("commission"))["total"] or Decimal("0"),
            "tasks": Reminder.objects.filter(agent=agent, completed=False).count(),
        })
    return rows


def get_notifications():
    today = date.today()
    return Reminder.objects.filter(completed=False, due_date__lte=today).select_related("agent")


def minimal_pdf(lines):
    def esc(text):
        return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    content = ["BT", "/F1 14 Tf", "50 780 Td"]
    for index, line in enumerate(lines):
        if index:
            content.append("0 -24 Td")
        content.append(f"({esc(line)}) Tj")
    content.append("ET")
    stream = "\n".join(content).encode()
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        b"5 0 obj << /Length " + str(len(stream)).encode() + b" >> stream\n" + stream + b"\nendstream endobj\n",
    ]
    pdf = b"%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj
    xref = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n".encode()
    pdf += f"trailer << /Root 1 0 R /Size {len(objects) + 1} >>\nstartxref\n{xref}\n%%EOF".encode()
    return pdf
