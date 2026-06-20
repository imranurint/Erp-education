cd /var/www/others/ERP/mie_pathways

# Migrations for notifications app
python manage.py makemigrations notifications
python manage.py migrate

# Create media directories
mkdir -p media/receipts media/payslips media/reports media/statements media/invoices

# ── Start Redis (if not running) ──
sudo systemctl start redis
redis-cli ping  # should return PONG

# ── Start Celery Worker (new terminal) ──
celery -A mie_pathways worker -l info

# ── Start Celery Beat (new terminal) ──
celery -A mie_pathways beat -l info

# ── Start Django (new terminal) ──
python manage.py runserver