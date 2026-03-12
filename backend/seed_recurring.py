from api.models import RecurringTask

if RecurringTask.objects.count() == 0:
    defaults = [
        {'name': 'Water Tank Cleaning',   'area': 'Rooftop Tank',    'recurrence_type': 'monthly',   'recurrence_value': '15', 'time': '09:00:00', 'importance': 'medium'},
        {'name': 'Kitchen Deep Clean',    'area': 'Main Kitchen',    'recurrence_type': 'weekly',    'recurrence_value': '0',  'time': '22:00:00', 'importance': 'medium'},
        {'name': 'Food Waste Management', 'area': 'Waste Area',      'recurrence_type': 'daily',     'recurrence_value': '',   'time': '22:00:00', 'importance': 'low'},
        {'name': 'General Cleaning',      'area': 'All Blocks',      'recurrence_type': 'weekly',    'recurrence_value': '1,4','time': '10:00:00', 'importance': 'low'},
        {'name': 'Pest Control',          'area': 'All Floors',      'recurrence_type': 'monthly',   'recurrence_value': '1',  'time': '08:00:00', 'importance': 'high'},
        {'name': 'Fire Safety Audit',     'area': 'Entire Hostel',   'recurrence_type': 'quarterly', 'recurrence_value': '',   'time': '10:00:00', 'importance': 'high'},
        {'name': 'Inventory Restock',     'area': 'Storeroom',       'recurrence_type': 'biweekly',  'recurrence_value': '1',  'time': '11:00:00', 'importance': 'low'},
    ]
    for d in defaults:
        RecurringTask.objects.create(**d)
    print('Seeded', len(defaults), 'recurring tasks')
else:
    print('Already seeded:', RecurringTask.objects.count(), 'tasks')
