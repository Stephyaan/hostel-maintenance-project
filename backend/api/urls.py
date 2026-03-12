from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, ComplaintViewSet, WorkerViewSet, ResourceRequestViewSet, NoticeViewSet, GlobalSettingViewSet, MaintenanceScheduleViewSet, ExportLogViewSet, MaintenanceCategoryViewSet, RecurringTaskViewSet, ScheduleNotificationViewSet, SystemHealthViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'complaints', ComplaintViewSet, basename='complaint')
router.register(r'workers', WorkerViewSet, basename='worker')
router.register(r'resource-requests', ResourceRequestViewSet, basename='resource')
router.register(r'notices', NoticeViewSet, basename='notice')
router.register(r'settings', GlobalSettingViewSet, basename='setting')
router.register(r'schedules', MaintenanceScheduleViewSet, basename='schedule')
router.register(r'export-logs', ExportLogViewSet, basename='exportlog')
router.register(r'categories', MaintenanceCategoryViewSet, basename='category')
router.register(r'recurring-tasks', RecurringTaskViewSet, basename='recurringtask')
router.register(r'schedule-notifications', ScheduleNotificationViewSet, basename='schedulenotif')
router.register(r'system-health', SystemHealthViewSet, basename='systemhealth')

urlpatterns = [
    path('', include(router.urls)),
]
