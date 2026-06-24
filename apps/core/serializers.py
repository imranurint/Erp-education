from rest_framework import serializers
from .models import (
    Asset, AssetAssignment, AssetCategory, AssetDepreciation, AssetMaintenance, Branch, User, UserSession, ExchangeRate,
    Setting, Notification, AuditLog
)


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'user_id', 'name', 'email', 'role', 'branch', 'branch_name',
            'phone', 'status', 'last_login', 'two_factor_enabled',
            'is_active', 'created_at',
        ]
        read_only_fields = ['user_id', 'last_login', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'user_id', 'name', 'email', 'password', 'role',
            'branch', 'phone',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Wrong current password')
        return value


class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = '__all__'


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['notification_id', 'user', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['log_id', 'created_at']



### ASSETS

class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = '__all__'


class AssetListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.category_name', read_only=True
    )
    assigned_to = serializers.CharField(
        source='assigned_employee.user.name', read_only=True, default=None
    )
    branch_name = serializers.CharField(
        source='assigned_branch.branch_name', read_only=True, default=None
    )

    class Meta:
        model = Asset
        fields = [
            'asset_id', 'asset_code', 'asset_name', 'category',
            'category_name', 'purchase_date', 'purchase_price',
            'current_value', 'accumulated_depreciation',
            'condition', 'status', 'assigned_to', 'assigned_branch',
            'branch_name', 'location',
        ]


class AssetDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.category_name', read_only=True
    )
    assigned_employee_name = serializers.CharField(
        source='assigned_employee.user.name', read_only=True, default=None
    )
    assigned_branch_name = serializers.CharField(
        source='assigned_branch.branch_name', read_only=True, default=None
    )
    branch_name = serializers.CharField(
        source='branch.branch_name', read_only=True, default=None
    )
    depreciation_history = serializers.SerializerMethodField()
    maintenance_history = serializers.SerializerMethodField()
    assignment_history = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = '__all__'

    def get_depreciation_history(self, obj):
        records = AssetDepreciation.objects.filter(asset=obj).order_by('-depreciation_date')[:12]
        return AssetDepreciationSerializer(records, many=True).data

    def get_maintenance_history(self, obj):
        records = AssetMaintenance.objects.filter(asset=obj).order_by('-maintenance_date')[:12]
        return AssetMaintenanceSerializer(records, many=True).data

    def get_assignment_history(self, obj):
        records = AssetAssignment.objects.filter(asset=obj).order_by('-assigned_date')[:12]
        return AssetAssignmentSerializer(records, many=True).data


class AssetDepreciationSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.asset_name', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)

    class Meta:
        model = AssetDepreciation
        fields = '__all__'


class AssetMaintenanceSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.asset_name', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)

    class Meta:
        model = AssetMaintenance
        fields = '__all__'


class AssetAssignmentSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.asset_name', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    employee_name = serializers.CharField(
        source='employee.user.name', read_only=True
    )
    employee_code = serializers.CharField(
        source='employee.employee_code', read_only=True
    )

    class Meta:
        model = AssetAssignment
        fields = '__all__'