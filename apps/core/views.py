from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Asset, AssetAssignment, AssetCategory, AssetMaintenance, Branch, User, ExchangeRate, Setting, Notification, AuditLog
)
from .serializers import (
    AssetAssignmentSerializer, AssetCategorySerializer, AssetDetailSerializer, AssetListSerializer, AssetMaintenanceSerializer, BranchSerializer, UserSerializer, UserCreateSerializer,
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




## AssetViewSet
class AssetCategoryViewSet(viewsets.ModelViewSet):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    filterset_fields = ['status']
    search_fields = ['category_name']


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related(
        'category', 'assigned_employee__user',
        'assigned_branch', 'branch'
    ).all()
    filterset_fields = [
        'category', 'status', 'condition',
        'assigned_branch', 'branch', 'depreciation_method',
    ]
    search_fields = ['asset_code', 'asset_name', 'serial_number', 'manufacturer']
    ordering_fields = ['asset_code', 'purchase_date', 'purchase_price', 'current_value']

    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        return AssetDetailSerializer

    @action(detail=True, methods=['get'])
    def depreciation(self, request, pk=None):
        """GET /api/v1/assets/{id}/depreciation/"""
        asset = self.get_object()
        records = AssetDepreciation.objects.filter(
            asset=asset
        ).order_by('-depreciation_date')
        return Response(AssetDepreciationSerializer(records, many=True).data)

    @action(detail=True, methods=['get'])
    def maintenance(self, request, pk=None):
        """GET /api/v1/assets/{id}/maintenance/"""
        asset = self.get_object()
        records = AssetMaintenance.objects.filter(
            asset=asset
        ).order_by('-maintenance_date')
        return Response(AssetMaintenanceSerializer(records, many=True).data)

    @action(detail=True, methods=['get'])
    def assignments(self, request, pk=None):
        """GET /api/v1/assets/{id}/assignments/"""
        asset = self.get_object()
        records = AssetAssignment.objects.filter(
            asset=asset
        ).order_by('-assigned_date')
        return Response(AssetAssignmentSerializer(records, many=True).data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        POST /api/v1/assets/{id}/assign/
        Body: {"employee_id": 5, "notes": "For daily teaching use"}
        """
        asset = self.get_object()
        employee_id = request.data.get('employee_id')
        notes = request.data.get('notes', '')

        from apps.hrm.models import Employee
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=400)

        # Close previous active assignment
        AssetAssignment.objects.filter(
            asset=asset, status='Active'
        ).update(
            status='Returned',
            return_date=date.today(),
            condition_at_return=asset.condition,
        )

        # Create new assignment
        assignment = AssetAssignment.objects.create(
            asset=asset, employee=employee,
            assigned_date=date.today(),
            condition_at_assignment=asset.condition,
            notes=notes,
            assigned_by=request.user,
            branch=asset.branch,
        )

        # Update asset
        asset.assigned_employee = employee
        asset.save(update_fields=['assigned_employee', 'updated_at'])

        return Response(AssetAssignmentSerializer(assignment).data)

    @action(detail=True, methods=['post'])
    def return_asset(self, request, pk=None):
        """
        POST /api/v1/assets/{id}/return_asset/
        Body: {"condition": "Good", "notes": "Returned in good condition"}
        """
        asset = self.get_object()
        condition = request.data.get('condition', 'Good')
        notes = request.data.get('notes', '')

        assignment = AssetAssignment.objects.filter(
            asset=asset, status='Active'
        ).first()

        if assignment:
            assignment.status = 'Returned'
            assignment.return_date = date.today()
            assignment.condition_at_return = condition
            assignment.notes = notes
            assignment.save()

        asset.assigned_employee = None
        asset.condition = condition
        asset.save(update_fields=['assigned_employee', 'condition', 'updated_at'])

        return Response(AssetDetailSerializer(asset).data)

    @action(detail=True, methods=['post'])
    def dispose(self, request, pk=None):
        """
        POST /api/v1/assets/{id}/dispose/
        Body: {"disposal_amount": 5000, "notes": "Sold to scrap dealer"}
        """
        asset = self.get_object()
        disposal_amount = request.data.get('disposal_amount', 0)
        notes = request.data.get('notes', '')

        asset.status = 'Disposed'
        asset.disposal_date = date.today()
        asset.disposal_amount = disposal_amount
        asset.assigned_employee = None
        asset.notes = notes
        asset.save()

        # Loss on disposal = current_value - disposal_amount
        return Response(AssetDetailSerializer(asset).data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        GET /api/v1/assets/summary/
        Returns aggregate asset data.
        """
        from django.db.models import Sum, Count
        branch_id = request.query_params.get('branch_id')

        qs = Asset.objects.filter(status__in=['Active', 'Under Maintenance'])
        if branch_id:
            qs = qs.filter(assigned_branch_id=branch_id)

        summary = qs.aggregate(
            total_assets=Count('asset_id'),
            total_purchase_value=Sum('purchase_price'),
            total_current_value=Sum('current_value'),
            total_depreciation=Sum('accumulated_depreciation'),
        )

        by_category = qs.values(
            'category__category_name'
        ).annotate(
            count=Count('asset_id'),
            value=Sum('current_value'),
        ).order_by('-value')

        by_branch = qs.values(
            'assigned_branch__branch_name'
        ).annotate(
            count=Count('asset_id'),
            value=Sum('current_value'),
        ).order_by('-value')

        by_condition = qs.values('condition').annotate(
            count=Count('asset_id'),
        )

        by_status = Asset.objects.values('status').annotate(
            count=Count('asset_id'),
        )

        return Response({
            **summary,
            'by_category': list(by_category),
            'by_branch': list(by_branch),
            'by_condition': list(by_condition),
            'by_status': list(by_status),
        })


class AssetMaintenanceViewSet(viewsets.ModelViewSet):
    queryset = AssetMaintenance.objects.select_related('asset').all()
    serializer_class = AssetMaintenanceSerializer
    filterset_fields = ['asset', 'maintenance_type', 'status', 'branch']
    search_fields = ['asset__asset_name', 'description', 'vendor']
    ordering_fields = ['maintenance_date', 'cost']


class AssetAssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssetAssignment.objects.select_related(
        'asset', 'employee__user'
    ).all()
    serializer_class = AssetAssignmentSerializer
    filterset_fields = ['asset', 'employee', 'status', 'branch']
    search_fields = ['asset__asset_name', 'employee__user__name']