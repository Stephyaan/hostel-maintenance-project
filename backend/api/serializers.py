from rest_framework import serializers
from .models import User, Complaint, Worker, ResourceRequest, Notice, GlobalSetting, MaintenanceSchedule, ExportLog, MaintenanceCategory, RecurringTask, ScheduleNotification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'room_number', 'block', 'first_name', 'last_name']

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'

class ComplaintSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    assigned_worker_name = serializers.CharField(source='assigned_worker.name', read_only=True)
    etr_hours = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ['student', 'assigned_worker_name', 'created_at', 'updated_at']

    def get_student_name(self, obj):
        if obj.is_anonymous:
            return "Anonymous Student"
        return obj.student.username if obj.student else "Unknown"

    def get_etr_hours(self, obj):
        if obj.category:
            cat = MaintenanceCategory.objects.filter(name=obj.category).first()
            if cat:
                return cat.etr_hours
        return 24 # Fallback default

class ResourceRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = ResourceRequest
        fields = '__all__'
        read_only_fields = ['student', 'student_name', 'created_at']

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'

class GlobalSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSetting
        fields = ['id', 'key', 'value', 'description']

class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceSchedule
        fields = '__all__'

class ExportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportLog
        fields = '__all__'

class MaintenanceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceCategory
        fields = '__all__'

class RecurringTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringTask
        fields = '__all__'

class ScheduleNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleNotification
        fields = '__all__'
