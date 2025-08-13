"""
Cron job setup for commission automation

To set up automated commission calculation and dealer deactivation:

1. Add to your crontab (run `crontab -e`):

# Calculate commissions monthly (1st day of each month at 2:00 AM)
0 2 1 * * /path/to/your/python /path/to/manage.py calculate_commissions

# Check for overdue dealers daily (every day at 3:00 AM)
0 3 * * * /path/to/your/python /path/to/manage.py deactivate_overdue_dealers

# Generate next month commissions for dealers who paid within 30 days (daily at 4:00 AM)
0 4 * * * /path/to/your/python /path/to/manage.py generate_next_month_commissions

2. Or use Django-crontab package:

Install: pip install django-crontab

Add to INSTALLED_APPS in settings.py:
INSTALLED_APPS = [
    ...
    'django_crontab',
    ...
]

Add to settings.py:
CRONJOBS = [
    ('0 2 1 * *', 'invoice.management.commands.calculate_commissions.Command'),
    ('0 3 * * *', 'invoice.management.commands.deactivate_overdue_dealers.Command'),
    ('0 4 * * *', 'invoice.management.commands.generate_next_month_commissions.Command'),
]

Then run:
python manage.py crontab add
python manage.py crontab show  # to verify

3. Or use Celery with periodic tasks:

Install: pip install celery django-celery-beat

Configure periodic tasks in settings.py or admin panel.
"""

# Example Celery tasks (create tasks.py in invoice app)
from celery import shared_task
from django.core.management import call_command

@shared_task
def calculate_monthly_commissions():
    """Celery task to calculate monthly commissions"""
    call_command('calculate_commissions')

@shared_task  
def check_overdue_dealers():
    """Celery task to deactivate overdue dealers"""
    call_command('deactivate_overdue_dealers')

@shared_task  
def generate_next_month_commissions():
    """Celery task to generate next month commissions for dealers who paid within 30 days"""
    call_command('generate_next_month_commissions')
