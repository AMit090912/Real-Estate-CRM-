# Django Deployment Notes

This assignment runs locally with SQLite and `DEBUG=True`. For production, use the following setup.

## Server

1. Create a Python virtual environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Set environment-specific values for:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS`
   - database credentials

4. Run:

```powershell
python manage.py migrate
python manage.py collectstatic
```

5. Serve with Gunicorn/Uvicorn behind Nginx, Apache, or a cloud load balancer.

## Database

SQLite is fine for assignment review. Production should use PostgreSQL or MySQL.

## Media Files

Local media works for this prototype. Production should use S3, Azure Blob Storage, or Google Cloud Storage.

## Security

- Use HTTPS.
- Use a strong `SECRET_KEY`.
- Set `DEBUG=False`.
- Set secure cookies.
- Keep CSRF protection enabled.
- Use Django auth groups/permissions for a full production RBAC setup.

## Backup

For the local assignment:

```powershell
Copy-Item db.sqlite3 backups\db-$(Get-Date -Format yyyyMMdd-HHmmss).sqlite3
```

For production, schedule database and media backups with restore testing.
