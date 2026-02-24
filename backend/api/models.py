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
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} - {self.status}"

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
    value = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.key}: {self.value}"
