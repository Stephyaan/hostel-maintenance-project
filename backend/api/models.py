from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    room_number = models.CharField(max_length=20, blank=True, null=True)  # For students
    block = models.CharField(max_length=10, blank=True, null=True)        # For students

    def __str__(self):
        return f"{self.username} ({self.role})"

# 2. Workers
class Worker(models.Model):
    name = models.CharField(max_length=100)
    skill = models.CharField(max_length=50)  # Plumbing, Electrical, etc.
    phone = models.CharField(max_length=15)
    is_available = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True) # Default to True, but will be False if settings require it
    is_active = models.BooleanField(default=True) # Whether the worker is currently on the roster

    def __str__(self):
        return f"{self.name} - {self.skill}"

# 3. Complaints
class Complaint(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Awaiting Approval', 'Awaiting Approval'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    )
    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    room = models.CharField(max_length=50) # Snapshot of room at time of complaint
    category = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Low')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints', null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    assigned_worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Feedback
    feedback_rating = models.IntegerField(null=True, blank=True)
    feedback_comment = models.TextField(null=True, blank=True)

    # Proof of resolution
    resolution_proof = models.TextField(null=True, blank=True) # Base64 or URL

    is_duplicate = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.status})"

# 4. Resource Requests
class ResourceRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    urgency = models.CharField(max_length=20, default='Normal')
    description = models.TextField(blank=True, null=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    # Feedback
    feedback_rating = models.IntegerField(null=True, blank=True)
    feedback_comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.item_name} ({self.quantity}) - {self.status}"

# 5. Notices
class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 6. Global Settings
class GlobalSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField(default=dict)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.key}: {self.value}"

class MaintenanceSchedule(models.Model):
    title = models.CharField(max_length=200)
    area = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    importance = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='low')
    is_done = models.BooleanField(default=False)
    worker = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    recurring_task = models.ForeignKey('RecurringTask', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.date}"

class ExportLog(models.Model):
    report_type = models.CharField(max_length=100)
    generated_by = models.CharField(max_length=50, default='Supervisor')
    date_generated = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Completed')

    def __str__(self):
        return f"{self.report_type} by {self.generated_by} at {self.date_generated}"

class MaintenanceCategory(models.Model):
    name = models.CharField(max_length=100)
    default_priority = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], default='Low')
    etr_hours = models.IntegerField(default=24)

    def __str__(self):
        return self.name



class RecurringTask(models.Model):
    RECURRENCE_CHOICES = [
        ('daily',     'Daily'),
        ('weekly',    'Weekly'),
        ('biweekly',  'Every 2 Weeks'),
        ('monthly',   'Monthly'),
        ('quarterly', 'Every 3 Months'),
    ]
    IMPORTANCE_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    name             = models.CharField(max_length=200)
    area             = models.CharField(max_length=100, blank=True, default='')
    recurrence_type  = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='weekly')
    # For weekly/biweekly: comma-separated JS weekday numbers (0=Sun,1=Mon,...,6=Sat)
    # For monthly: day-of-month as string e.g. "15"
    # For daily/quarterly: empty string
    recurrence_value = models.CharField(max_length=100, blank=True, default='')
    time             = models.TimeField(blank=True, null=True)
    importance       = models.CharField(max_length=20, choices=IMPORTANCE_CHOICES, default='low')
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.recurrence_type})"

    def generate_schedules(self, days_ahead=30):
        """Generates MaintenanceSchedule entries for this recurring task."""
        from datetime import date, timedelta
        
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        current = today
        
        while current <= end_date:
            if self.is_due_on(current):
                # Check if schedule already exists for this date/task
                exists = MaintenanceSchedule.objects.filter(
                    recurring_task=self,
                    date=current
                ).exists()
                
                if not exists:
                    MaintenanceSchedule.objects.create(
                        title=self.name,
                        area=self.area,
                        date=current,
                        time=self.time,
                        importance=self.importance,
                        recurring_task=self,
                        notes=f"Auto-generated: {self.get_recurrence_type_display()}"
                    )
            current += timedelta(days=1)

    def is_due_on(self, check_date):
        if not self.is_active: return False
        
        if self.recurrence_type == 'daily':
            return True
        
        if self.recurrence_type == 'weekly':
            # recurrence_value is "1,4" for Mon, Thu
            days = [int(x.strip()) for x in self.recurrence_value.split(',') if x.strip().isdigit()]
            # check_date.weekday() where 0=Mon, 6=Sun. 
            # RecurringTask uses JS weekday: 0=Sun, 1=Mon...6=Sat
            js_weekday = (check_date.weekday() + 1) % 7
            return js_weekday in days
            
        if self.recurrence_type == 'biweekly':
            days = [int(x.strip()) for x in self.recurrence_value.split(',') if x.strip().isdigit()]
            js_weekday = (check_date.weekday() + 1) % 7
            if js_weekday not in days: return False
            # Check if it's an even week from a fixed epoch
            from datetime import date as dte
            epoch = dte(2024, 1, 1) # A Monday
            delta_weeks = (check_date - epoch).days // 7
            return delta_weeks % 2 == 0
            
        if self.recurrence_type == 'monthly':
            try:
                day_val = int(self.recurrence_value)
                return check_date.day == day_val
            except:
                return False
                
        if self.recurrence_type == 'quarterly':
            # Every 3 months (Jan, Apr, Jul, Oct) on 1st
            return check_date.month in [1, 4, 7, 10] and check_date.day == 1
            
        return False


class ScheduleNotification(models.Model):
    TYPE_CHOICES = [
        ('missed',   'Missed Task'),
        ('reminder', 'Reminder'),
        ('info',     'Info'),
    ]
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='missed')
    is_read    = models.BooleanField(default=False)
    # Optional: mark done by supervisor (acknowledged + actioned)
    is_done    = models.BooleanField(default=False)
    sent_by    = models.CharField(max_length=100, default='Admin')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notif_type}] {self.title}"
