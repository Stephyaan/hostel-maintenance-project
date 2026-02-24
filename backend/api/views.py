from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from .models import User, Complaint, Worker, ResourceRequest, Notice, GlobalSetting
from .serializers import UserSerializer, ComplaintSerializer, WorkerSerializer, ResourceRequestSerializer, NoticeSerializer, GlobalSettingSerializer

# AUTH VIEWSET (Login/Logout)
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
        # Auto-assign the logged-in user as the student
        serializer.save(student=self.request.user)

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
        # Check if autonomous registration is disabled
        auto_reg = GlobalSetting.objects.filter(key='autonomous_staff_registration').first()
        is_approved = True
        if auto_reg and auto_reg.value == False:
            is_approved = False
        serializer.save(is_approved=is_approved)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Worker.objects.all()
        # Supervisors and students only see approved workers
        return Worker.objects.filter(is_approved=True)

# RESOURCE REQUEST VIEWSET
class ResourceRequestViewSet(viewsets.ModelViewSet):
    queryset = ResourceRequest.objects.all()
    serializer_class = ResourceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
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

