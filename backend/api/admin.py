from django.contrib import admin
from .models import User, Complaint, Worker, ResourceRequest, Notice

admin.site.register(User)
admin.site.register(Worker)
admin.site.register(Complaint)
admin.site.register(ResourceRequest)
admin.site.register(Notice)
