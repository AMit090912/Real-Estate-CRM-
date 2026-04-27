# Real Estate CRM Module - Django Version

This is the Django implementation of the HR assignment. It keeps the UI simple and uses normal Django pages/forms so Save buttons submit reliably.

## Tech Stack

- Backend: Python + Django 5.2
- Frontend: Django templates + simple CSS
- Database: SQLite
- File uploads: Django `FileField` under `media/`
- Reports: Dashboard, agent reports, CSV export, PDF export
- Integrations: Website capture form + JSON webhook endpoints

## Run

Use the bundled Python runtime:

```powershell
& 'C:\Users\khemc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' manage.py runserver 127.0.0.1:3000
```

Open:

```text
http://localhost:3000
```

## Setup Commands

These are already done, but they are included for review:

```powershell
& 'C:\Users\khemc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' manage.py migrate
& 'C:\Users\khemc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' manage.py seed_demo
```

## Test

```powershell
& 'C:\Users\khemc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' manage.py test crm
```

Current result:

```text
Ran 4 tests in 0.332s
OK
```

## Covered Assignment Tasks

| Requirement | Django implementation |
| --- | --- |
| CRM Web App | Django templates and views |
| Admin Dashboard | `/` dashboard with KPIs and notifications |
| Agent Panel | `/agents/`, assigned leads, reminders and performance |
| Lead Management | `/leads/` CRUD, status workflow, assignment, follow-up reminders |
| Property Management | `/properties/` CRUD, image upload/URL, filters, maps |
| Client Management | `/clients/` buyer/seller profiles, visits and inquiries |
| Deal Management | `/deals/` Kanban pipeline, stage changes, commission calculation, document upload |
| Communication | `/communications/` activity log and follow-up scheduler |
| Reports | `/reports/`, CSV export, PDF export |
| Integrations | `/integrations/`, `/api/leads/capture/`, `/api/webhooks/lead/` |
| Roles | Role switcher for Admin, Manager and Agent permissions |
| Mobile | Responsive layout in `crm/static/crm/style.css` |

## Important Files

- `manage.py`
- `estatecrm/settings.py`
- `crm/models.py`
- `crm/views.py`
- `crm/forms.py`
- `crm/urls.py`
- `crm/templates/crm/`
- `crm/static/crm/style.css`
- `crm/tests.py`
- `crm/management/commands/seed_demo.py`

## Notes

Django is installed locally in the `vendor/` folder because this environment did not have Django preinstalled. For normal development, you can also install dependencies from `requirements.txt` in a virtual environment.
