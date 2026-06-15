from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Branch, User, ExchangeRate, Setting, Notification, AuditLog
)
from .serializers import (
    BranchSerializer, UserSerializer, UserCreateSerializer,
    ChangePasswordSerializer, ExchangeRateSerializer,
    SettingSerializer, NotificationSerializer, AuditLogSerializer
)


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    filterset_fields = ['status', 'city']
    search_fields = ['branch_name', 'branch_code', 'city']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('branch').all()
    filterset_fields = ['role', 'branch', 'status']
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Password changed'})


class ExchangeRateViewSet(viewsets.ModelViewSet):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    filterset_fields = ['from_currency', 'to_currency']
    ordering_fields = ['effective_date', 'rate']


class SettingViewSet(viewsets.ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    filterset_fields = ['category', 'branch']
    search_fields = ['setting_key', 'setting_value']


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'message': 'All marked as read'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'message': 'Marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    filterset_fields = ['action', 'table_name', 'user', 'branch']
    search_fields = ['description', 'table_name']
    ordering_fields = ['created_at']
