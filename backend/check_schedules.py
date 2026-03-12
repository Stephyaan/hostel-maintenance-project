import os, django, sys
sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_backend.settings')
django.setup()

from api.models import MaintenanceSchedule
from datetime import date

print(f'Today: {date.today()}')
print(f'Total schedules in DB: {MaintenanceSchedule.objects.count()}')
print()

for s in MaintenanceSchedule.objects.all().order_by('date', 'time'):
    done = 'DONE' if s.is_done else 'PENDING'
    is_today = ' <-- TODAY' if s.date == date.today() else ''
    print(f'  [{done}] {s.date} {s.time or "All Day"} | {s.title} | {s.area} | {s.importance}{is_today}')
