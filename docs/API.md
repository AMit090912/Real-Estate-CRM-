# Django CRM API Notes

The main app is server-rendered with Django templates. These lightweight JSON endpoints are included for assignment integration requirements.

Base URL:

```text
http://localhost:3000
```

## Lead Capture

### POST `/api/leads/capture/`

Creates a new lead, assigns it to the least-loaded active agent, and creates a first-contact reminder.

```json
{
  "name": "Website Visitor",
  "phone": "+91 90000 00000",
  "email": "visitor@example.com",
  "source": "Website",
  "budget": 9000000,
  "preferences": "2 BHK near metro"
}
```

Response:

```json
{
  "id": 1,
  "name": "Website Visitor",
  "assigned_agent": "Nisha Rao"
}
```

## Webhook

### POST `/api/webhooks/lead/`

Same behavior as lead capture, intended for third-party portals.

## Report Exports

### GET `/reports/export/csv/`

Downloads a CSV report with KPI and agent performance rows.

### GET `/reports/export/pdf/`

Downloads a simple PDF report.

## Main Django Pages

- `/` dashboard
- `/leads/`
- `/properties/`
- `/clients/`
- `/deals/`
- `/communications/`
- `/agents/`
- `/reports/`
- `/integrations/`
- `/admin/`
