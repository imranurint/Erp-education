from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Permission, Group





class Branch(models.Model):
    branch_id = models.AutoField(primary_key=True)
    branch_code = models.CharField(max_length=10, unique=True)
    branch_name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    status = models.CharField(
        max_length=8,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive')],
        default='Active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'branches'
        ordering = ['branch_name']

    def __str__(self):
        return f"{self.branch_code} - {self.branch_name}"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'Super Admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Super Admin', 'Super Admin'),
        ('Branch Admin', 'Branch Admin'),
        ('Accountant', 'Accountant'),
        ('Collector', 'Collector'),
        ('Counselor', 'Counselor'),
        ('Academic', 'Academic'),
    ]

    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    branch = models.ForeignKey(
        Branch, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='branch_id'
    )
    phone = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(
        max_length=8,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Locked', 'Locked')],
        default='Active'
    )
    last_login = models.DateTimeField(blank=True, null=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    password_changed_at = models.DateTimeField(blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'role']

    class Meta:
        db_table = 'users'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.role})"


class UserSession(models.Model):
    session_id = models.CharField(primary_key=True, max_length=128)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='user_id')
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_sessions'


class ExchangeRate(models.Model):
    rate_id = models.AutoField(primary_key=True)
    from_currency = models.CharField(max_length=3)
    to_currency = models.CharField(max_length=3, default='BDT')
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    effective_date = models.DateField()
    source = models.CharField(max_length=100, blank=True, null=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='branch_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='created_by'
    )

    class Meta:
        db_table = 'exchange_rates'
        unique_together = [('from_currency', 'to_currency', 'effective_date')]
        ordering = ['-effective_date']


class Setting(models.Model):
    setting_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=50)
    setting_key = models.CharField(max_length=100)
    setting_value = models.TextField(blank=True, null=True)
    value_type = models.CharField(
        max_length=7,
        choices=[
            ('String', 'String'), ('Integer', 'Integer'),
            ('Decimal', 'Decimal'), ('Boolean', 'Boolean'), ('JSON', 'JSON'),
        ],
        default='String'
    )
    description = models.CharField(max_length=300, blank=True, null=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='branch_id'
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='updated_by'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settings'
        unique_together = [('category', 'setting_key', 'branch')]


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='user_id')
    type = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    message = models.TextField()
    reference_type = models.CharField(max_length=50, blank=True, null=True)
    reference_id = models.IntegerField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='branch_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']


class AuditLog(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='user_id'
    )
    action = models.CharField(max_length=12)
    table_name = models.CharField(max_length=100)
    record_id = models.IntegerField()
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='branch_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_log'
        ordering = ['-created_at']









###ASSET MODEL

class AssetCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    depreciation_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text='Annual depreciation percentage (e.g. 20.00 = 20%)'
    )
    useful_life_years = models.IntegerField(
        default=5, help_text='Useful life in years'
    )
    coa_asset_account = models.ForeignKey(
        'accounting.ChartOfAccount', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='asset_category_asset',
        help_text='Asset account in COA (e.g. 1210 Office Equipment)'
    )
    coa_depreciation_account = models.ForeignKey(
        'accounting.ChartOfAccount', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='asset_category_depreciation',
        help_text='Accumulated depreciation account (e.g. 1211)'
    )
    coa_expense_account = models.ForeignKey(
        'accounting.ChartOfAccount', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='asset_category_expense',
        help_text='Depreciation expense account (e.g. 5701)'
    )
    status = models.CharField(max_length=8, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asset_categories'
        ordering = ['category_name']
        verbose_name_plural = 'Asset Categories'

    def __str__(self):
        return self.category_name


class Asset(models.Model):
    asset_id = models.AutoField(primary_key=True)
    asset_code = models.CharField(max_length=30, unique=True)
    asset_name = models.CharField(max_length=200)
    category = models.ForeignKey(
        AssetCategory, on_delete=models.CASCADE
    )
    description = models.TextField(blank=True, null=True)
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2)
    salvage_value = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Estimated value at end of useful life'
    )
    current_value = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text='Current book value (purchase - accumulated depreciation)'
    )
    accumulated_depreciation = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    depreciation_method = models.CharField(
        max_length=20, default='Straight Line',
        choices=[
            ('Straight Line', 'Straight Line'),
            ('Declining Balance', 'Declining Balance'),
            ('None', 'No Depreciation'),
        ]
    )
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    purchase_voucher = models.ForeignKey(
        'accounting.Voucher', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='purchased_assets'
    )
    assigned_employee = models.ForeignKey(
        'hrm.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_assets'
    )
    assigned_branch = models.ForeignKey(
        'core.Branch', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assets'
    )
    location = models.CharField(
        max_length=200, blank=True, null=True,
        help_text='Physical location (Room 201, 2nd Floor, etc.)'
    )
    condition = models.CharField(
        max_length=15, default='Good',
        choices=[
            ('Excellent', 'Excellent'),
            ('Good', 'Good'),
            ('Fair', 'Fair'),
            ('Poor', 'Poor'),
            ('Damaged', 'Damaged'),
        ]
    )
    status = models.CharField(
        max_length=55, default='Active',
        choices=[
            ('Active', 'Active'),
            ('Under Maintenance', 'Under Maintenance'),
            ('Disposed', 'Disposed'),
            ('Lost', 'Lost'),
            ('Retired', 'Retired'),
        ]
    )
    disposal_date = models.DateField(null=True, blank=True)
    disposal_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    notes = models.TextField(blank=True, null=True)
    photo_path = models.CharField(max_length=500, blank=True, null=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_assets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assets'
        ordering = ['asset_code']

    def __str__(self):
        return f"{self.asset_code} - {self.asset_name}"


class AssetDepreciation(models.Model):
    depreciation_id = models.AutoField(primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='depreciation_records')
    depreciation_date = models.DateField()
    period_label = models.CharField(
        max_length=20, help_text='e.g. "June 2026" or "2025-2026"'
    )
    opening_value = models.DecimalField(max_digits=15, decimal_places=2)
    depreciation_amount = models.DecimalField(max_digits=15, decimal_places=2)
    closing_value = models.DecimalField(max_digits=15, decimal_places=2)
    accumulated_total = models.DecimalField(max_digits=15, decimal_places=2)
    voucher = models.ForeignKey(
        'accounting.Voucher', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    status = models.CharField(
        max_length=50, default='Calculated',
        choices=[
            ('Calculated', 'Calculated'),
            ('Posted', 'Posted'),
            ('Reversed', 'Reversed'),
        ]
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asset_depreciation'
        ordering = ['-depreciation_date']
        unique_together = [('asset', 'period_label')]


class AssetMaintenance(models.Model):
    maintenance_id = models.AutoField(primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_date = models.DateField()
    maintenance_type = models.CharField(
        max_length=15, default='Preventive',
        choices=[
            ('Preventive', 'Preventive'),
            ('Corrective', 'Corrective'),
            ('Emergency', 'Emergency'),
            ('Upgrade', 'Upgrade'),
        ]
    )
    description = models.TextField()
    cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    vendor = models.CharField(max_length=200, blank=True, null=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    voucher = models.ForeignKey(
        'accounting.Voucher', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    status = models.CharField(
        max_length=52, default='Completed',
        choices=[
            ('Scheduled', 'Scheduled'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled'),
        ]
    )
    performed_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='asset_maintenance_done'
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asset_maintenance'
        ordering = ['-maintenance_date']


class AssetAssignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='assignment_history')
    employee = models.ForeignKey(
        'hrm.Employee', on_delete=models.CASCADE,
        related_name='asset_assignments'
    )
    assigned_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    condition_at_assignment = models.CharField(
        max_length=15, default='Good',
        choices=[
            ('Excellent', 'Excellent'), ('Good', 'Good'),
            ('Fair', 'Fair'), ('Poor', 'Poor'),
        ]
    )
    condition_at_return = models.CharField(max_length=15, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    assigned_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='asset_assignments_made'
    )
    status = models.CharField(
        max_length=50, default='Active',
        choices=[
            ('Active', 'Active'),
            ('Returned', 'Returned'),
            ('Transferred', 'Transferred'),
        ]
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asset_assignments'
        ordering = ['-assigned_date']