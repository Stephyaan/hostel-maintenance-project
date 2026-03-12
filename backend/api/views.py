from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from .models import User, Complaint, Worker, ResourceRequest, Notice, GlobalSetting, MaintenanceSchedule, ExportLog, MaintenanceCategory, RecurringTask, ScheduleNotification
from .serializers import UserSerializer, ComplaintSerializer, WorkerSerializer, ResourceRequestSerializer, NoticeSerializer, GlobalSettingSerializer, MaintenanceScheduleSerializer, ExportLogSerializer, MaintenanceCategorySerializer, RecurringTaskSerializer, ScheduleNotificationSerializer
from django.db import connection
from django.utils import timezone

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import models

# AUTH VIEWSET (Login/Logout)
@method_decorator(csrf_exempt, name='dispatch')
class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            return Response({'token': token.key, 'user': serializer.data})
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'success': 'Logged Out'})

# COMPLAINT VIEWSET
class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all().order_by('-created_at')
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        data = serializer.validated_data
        
        priority = data.get('priority', 'Low')
        
        # Rule-Based Priority Check
        priority_setting = GlobalSetting.objects.filter(key='rule_based_priority').first()
        if priority_setting and priority_setting.value == True:
            category_name = data.get('category')
            if category_name:
                cat = MaintenanceCategory.objects.filter(name=category_name).first()
                if cat:
                    priority = cat.default_priority

        # Duplicate Detection Check
        duplicate_setting = GlobalSetting.objects.filter(key='duplicate_detection').first()
        is_duplicate = False
        if duplicate_setting and duplicate_setting.value == True:
            from django.utils import timezone
            from datetime import timedelta
            yesterday = timezone.now() - timedelta(hours=24)
            room = data.get('room')
            if room:
                exists = Complaint.objects.filter(room=room, created_at__gte=yesterday).exists()
                if exists:
                    is_duplicate = True

        serializer.save(student=user, priority=priority, is_duplicate=is_duplicate)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        
        # Mandatory Proof of Resolution Check
        if data.get('status') == 'Resolved':
            setting = GlobalSetting.objects.filter(key='mandatory_resolution_proof').first()
            if setting and setting.value == True:
                # If mandatory, we MUST have resolution_proof
                if not data.get('resolution_proof') and not instance.resolution_proof:
                     return Response(
                         {'detail': 'Resolution Proof (photo/evidence) is required before marking as Resolved.'}, 
                         status=status.HTTP_400_BAD_REQUEST
                     )

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Complaint.objects.filter(student=user).order_by('-created_at')
        if user.role == 'supervisor' or user.role == 'admin':
            return Complaint.objects.all().order_by('-created_at')
        return Complaint.objects.none()

# WORKER VIEWSET
class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        from .models import GlobalSetting
        user = self.request.user
        
        # Admin bypass: If admin creates a worker, it defaults to approved
        if user.role == 'admin':
            serializer.save(is_approved=True)
            return

        # Check if approval is enabled for supervisors (ON = Needs Approval)
        auto_reg = GlobalSetting.objects.filter(key='autonomous_staff_registration').first()
        is_approved = True
        if auto_reg and auto_reg.value == True:
            is_approved = False
        serializer.save(is_approved=is_approved)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' or user.role == 'supervisor':
            return Worker.objects.all()
        # Students only see approved workers
        return Worker.objects.filter(is_approved=True)

# RESOURCE REQUEST VIEWSET
class ResourceRequestViewSet(viewsets.ModelViewSet):
    queryset = ResourceRequest.objects.all()
    serializer_class = ResourceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        from .models import GlobalSetting
        from rest_framework.exceptions import PermissionDenied
        
        # Check if module is enabled
        setting = GlobalSetting.objects.filter(key='resource_request_module').first()
        if setting and setting.value == False:
            raise PermissionDenied("Resource Request module is currently disabled by Admin.")
            
        serializer.save(student=self.request.user)

    def get_queryset(self):
        if self.request.user.role == 'student':
            return ResourceRequest.objects.filter(student=self.request.user)
        return ResourceRequest.objects.all()

# NOTICE VIEWSET
class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all().order_by('-created_at')
    serializer_class = NoticeSerializer

    def perform_create(self, serializer):
        from .models import GlobalSetting
        user = self.request.user
        
        # Determine if approval is needed based on settings
        is_approved = True
        if user.role != 'admin':
            setting = GlobalSetting.objects.filter(key='notice_approval_required').first()
            if setting and setting.value == True:
                is_approved = False
        
        serializer.save(created_by=user, is_approved=is_approved)

    def get_queryset(self):
        user = self.request.user
        qs = Notice.objects.filter(is_active=True).order_by('-created_at')
        
        # Students only see approved notices
        if not user.is_authenticated or user.role == 'student':
            return qs.filter(is_approved=True)
            
        # Supervisors see all notices but they might want to filter their own?
        # For now, Let's allow admins and supervisors to see all active notices
        # but filter for supervisors to see their own pending ones easily if needed.
        return qs

# SETTINGS VIEWSET
class GlobalSettingViewSet(viewsets.ModelViewSet):
    queryset = GlobalSetting.objects.all()
    serializer_class = GlobalSettingSerializer
    lookup_field = 'key'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        key = self.kwargs[lookup_url_kwarg]
        
        instance = GlobalSetting.objects.filter(key=key).first()
        
        # Merge key into data so validation passes
        data = request.data.copy()
        if 'key' not in data:
            data['key'] = key

        if instance is None:
            # Create if not exists
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

# SCHEDULE VIEWSET
class MaintenanceScheduleViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceSchedule.objects.all().order_by('date', 'time')
    serializer_class = MaintenanceScheduleSerializer

    def list(self, request):
        # Proactively generate from recurring tasks before listing
        for task in RecurringTask.objects.filter(is_active=True):
            task.generate_schedules(30)
        return super().list(request)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class ExportLogViewSet(viewsets.ModelViewSet):
    queryset = ExportLog.objects.all().order_by('-date_generated')
    serializer_class = ExportLogSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class MaintenanceCategoryViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceCategory.objects.all().order_by('name')
    serializer_class = MaintenanceCategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class RecurringTaskViewSet(viewsets.ModelViewSet):
    queryset = RecurringTask.objects.all().order_by('name')
    serializer_class = RecurringTaskSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def list(self, request):
        # Trigger generation for next 30 days
        for task in RecurringTask.objects.filter(is_active=True):
            task.generate_schedules(30)
        return super().list(request)

    def perform_create(self, serializer):
        task = serializer.save()
        task.generate_schedules(30)

    def perform_update(self, serializer):
        task = serializer.save()
        task.generate_schedules(30)

class ScheduleNotificationViewSet(viewsets.ModelViewSet):
    queryset = ScheduleNotification.objects.all().order_by('-created_at')
    serializer_class = ScheduleNotificationSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'status': 'marked read'})

    @action(detail=True, methods=['patch'])
    def mark_done(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.is_done = True
        notif.save()
        return Response({'status': 'marked done'})

    @action(detail=False, methods=['patch'])
    def mark_all_read(self, request):
        ScheduleNotification.objects.filter(is_read=False).update(is_read=True)
        return Response({'status': 'all marked read'})

# SYSTEM HEALTH VIEWSET
class SystemHealthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        # 1. Database Health
        db_ok = True
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            db_ok = False

        # 2. Operational Health (SLA Compliance & Avg Resolution)
        resolved = Complaint.objects.filter(status='Resolved')
        total_resolved = resolved.count()
        compliant_count = 0
        total_duration_hrs = 0

        cats = {c.name: c.etr_hours for c in MaintenanceCategory.objects.all()}

        for c in resolved:
            if c.created_at and c.updated_at:
                duration_hrs = (c.updated_at - c.created_at).total_seconds() / 3600
                total_duration_hrs += duration_hrs
                limit = cats.get(c.category, 24)
                if duration_hrs <= limit:
                    compliant_count += 1
        
        sla_rate = round((compliant_count / total_resolved * 100)) if total_resolved > 0 else 100
        avg_res_hrs = total_duration_hrs / total_resolved if total_resolved > 0 else 0
        avg_res_label = f"{round(avg_res_hrs)}h" if avg_res_hrs < 24 else f"{round(avg_res_hrs/24, 1)}d"

        # 3. Workforce Health
        total_workers = Worker.objects.count()
        available_workers = Worker.objects.filter(is_available=True).count()
        approved_workers = Worker.objects.filter(is_approved=True).count()
        workforce_load = available_workers / total_workers if total_workers > 0 else 1

        # 4. Feedback
        rated = Complaint.objects.filter(feedback_rating__gt=0)
        avg_feedback = rated.aggregate(avg=models.Avg('feedback_rating'))['avg'] or 0

        # 5. AUTO-GENERATE MISSED TASK ALERTS
        # Check all tasks in MaintenanceSchedule whose date is past and not is_done
        from datetime import date
        today = date.today()
        missed_tasks = MaintenanceSchedule.objects.filter(date__lt=today, is_done=False)
        
        alert_count = 0
        for task in missed_tasks:
            # check if a notification already exists for this missed task
            # Use task title and date in message for uniqueness
            notif_msg = f"The maintenance task '{task.title}' scheduled for {task.date} in {task.area} was missed."
            if not ScheduleNotification.objects.filter(title__contains=task.title, message__contains=str(task.date)).exists():
                ScheduleNotification.objects.create(
                    title=f"Missed Task: {task.title}",
                    message=notif_msg,
                    notif_type='missed',
                    sent_by='System'
                )
                alert_count += 1

        return Response({
            'database': 'Healthy' if db_ok else 'Error',
            'uptime': '99.9%',
            'operational_sla': sla_rate,
            'avg_resolution_time': avg_res_label,
            'workforce_availability': round(workforce_load * 100),
            'approved_workers': approved_workers,
            'pending_approval_workers': total_workers - approved_workers,
            'pending_issues': Complaint.objects.filter(status__in=['Pending', 'Awaiting Approval']).count(),
            'critical_shortages': ResourceRequest.objects.filter(status='Pending', urgency='Urgent').count(),
            'avg_feedback': round(float(avg_feedback), 1),
            'new_missed_alerts_generated': alert_count
        })

