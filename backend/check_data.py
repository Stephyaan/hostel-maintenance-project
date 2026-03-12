import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_backend.settings')
django.setup()

from api.models import MaintenanceCategory, Complaint

print('=== CATEGORIES ===')
for c in MaintenanceCategory.objects.all():
    print(f'  {c.name} (priority: {c.default_priority})')

print()
print('=== COMPLAINTS ===')
for c in Complaint.objects.all():
    print(f'  [{c.id}] {c.title} | category: "{c.category}" | status: {c.status}')
