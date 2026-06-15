from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Permission, Group


# Tell Django these tables exist but are not managed
class PermissionProxy(Permission):
    class Meta:
        db_table = 'auth_permission'
        managed = False


class GroupProxy(Group):
    class Meta:
        db_table = 'auth_group'
        managed = False



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
        managed = False
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
        managed = False
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
        managed = False


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
        managed = False
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
        managed = False
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
        managed = False
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
        managed = False
        ordering = ['-created_at']
