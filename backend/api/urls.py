from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, ComplaintViewSet, WorkerViewSet, ResourceRequestViewSet, NoticeViewSet, GlobalSettingViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'complaints', ComplaintViewSet, basename='complaint')
router.register(r'workers', WorkerViewSet, basename='worker')
router.register(r'resources', ResourceRequestViewSet, basename='resource')
router.register(r'notices', NoticeViewSet, basename='notice')
router.register(r'settings', GlobalSettingViewSet, basename='setting')

urlpatterns = [
    path('', include(router.urls)),
]
