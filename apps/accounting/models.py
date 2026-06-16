from django.db import models
from apps.core.models import Branch, User


class ChartOfAccount(models.Model):
    coa_id = models.AutoField(primary_key=True)
    coa_code = models.CharField(max_length=10, unique=True)
    coa_name = models.CharField(max_length=200)
    parent_code = models.CharField(max_length=10, blank=True, null=True)
    type = models.CharField(max_length=9)
    sub_type = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_system = models.BooleanField(default=False)
    is_cash_account = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=8, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chart_of_accounts'
        ordering = ['coa_code']

    def __str__(self):
        return f"{self.coa_code} - {self.coa_name}"


class ProgrammeFeeHead(models.Model):
    mapping_id = models.AutoField(primary_key=True)
    programme = models.ForeignKey(
        'academics.Programme', on_delete=models.DO_NOTHING, db_column='programme_id'
    )
    coa = models.ForeignKey(ChartOfAccount, on_delete=models.DO_NOTHING, db_column='coa_id')
    default_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_mandatory = models.BooleanField(default=True)
    is_installable = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'programme_fee_heads'


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    receipt_no = models.CharField(max_length=30, unique=True)
    student = models.ForeignKey('students.Student', on_delete=models.DO_NOTHING, db_column='student_id')
    date = models.DateField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)
    amount_in_bdt = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=15)
    transaction_ref = models.CharField(max_length=100, blank=True, null=True)
    bank_coa = models.ForeignKey(
        ChartOfAccount, on_delete=models.DO_NOTHING,
        blank=True, null=True, db_column='bank_coa_id'
    )
    collected_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='collected_by')
    approved_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='approved_by', related_name='approved_payments'
    )
    approved_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, default='Pending')
    rejection_reason = models.TextField(blank=True, null=True)
    reversal_reason = models.TextField(blank=True, null=True)
    reversed_payment = models.ForeignKey(
        'self', on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='reversed_payment_id'
    )
    remarks = models.TextField(blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column='branch_id')
    fiscal_period = models.ForeignKey(
        'academics.FiscalPeriod', on_delete=models.DO_NOTHING,
        blank=True, null=True, db_column='fiscal_period_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.receipt_no} - {self.total_amount}"


class PaymentItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, db_column='payment_id')
    due = models.ForeignKey(
        'students.StudentDue', on_delete=models.DO_NOTHING,
        blank=True, null=True, db_column='due_id'
    )
    coa = models.ForeignKey(ChartOfAccount, on_delete=models.DO_NOTHING, db_column='coa_id')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    remarks = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = 'payment_items'


class Voucher(models.Model):
    voucher_id = models.AutoField(primary_key=True)
    voucher_no = models.CharField(max_length=30, unique=True)
    voucher_type = models.CharField(max_length=10)
    date = models.DateField()
    narration = models.TextField()
    total_debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reference_type = models.CharField(max_length=50, blank=True, null=True)
    reference_id = models.IntegerField(blank=True, null=True)
    prepared_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='prepared_by')
    approved_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='approved_by', related_name='approved_vouchers'
    )
    approved_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, default='Draft')
    fiscal_period = models.ForeignKey(
        'academics.FiscalPeriod', on_delete=models.DO_NOTHING,
        blank=True, null=True, db_column='fiscal_period_id'
    )
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vouchers'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.voucher_no} ({self.voucher_type})"


class VoucherEntry(models.Model):
    entry_id = models.AutoField(primary_key=True)
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, db_column='voucher_id')
    line_number = models.IntegerField()
    coa = models.ForeignKey(ChartOfAccount, on_delete=models.DO_NOTHING, db_column='coa_id')
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    narration = models.CharField(max_length=500, blank=True, null=True)
    student = models.ForeignKey(
        'students.Student', on_delete=models.DO_NOTHING,
        blank=True, null=True, db_column='student_id'
    )
    partner = models.ForeignKey(
        'partners.Partner', on_delete=models.DO_NOTHING,
        blank=True, null=True, db_column='partner_id'
    )

    class Meta:
        db_table = 'voucher_entries'


class MainLedger(models.Model):
    ledger_id = models.BigAutoField(primary_key=True)
    entry_date = models.DateField()
    coa = models.ForeignKey(ChartOfAccount, on_delete=models.DO_NOTHING, db_column='coa_id')
    description = models.CharField(max_length=500, blank=True, null=True)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    reference_type = models.CharField(max_length=30)
    reference_id = models.IntegerField()
    voucher = models.ForeignKey(
        Voucher, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='voucher_id'
    )
    voucher_entry = models.ForeignKey(
        VoucherEntry, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='voucher_entry_id'
    )
    student = models.ForeignKey(
        'students.Student', on_delete=models.DO_NOTHING,
        blank=True, null=True, db_column='student_id'
    )
    fiscal_period = models.ForeignKey(
        'academics.FiscalPeriod', on_delete=models.DO_NOTHING,
        blank=True, null=True, db_column='fiscal_period_id'
    )
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'main_ledger'
        ordering = ['-entry_date']


class StudentLedger(models.Model):
    s_ledger_id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey('students.Student', on_delete=models.DO_NOTHING, db_column='student_id')
    entry_date = models.DateField()
    particulars = models.CharField(max_length=500)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    reference_type = models.CharField(max_length=30, blank=True, null=True)
    reference_id = models.IntegerField(blank=True, null=True)
    main_ledger = models.ForeignKey(
        MainLedger, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='main_ledger_id'
    )
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_ledger'
        ordering = ['entry_date']


class PettyCash(models.Model):
    cash_id = models.AutoField(primary_key=True)
    date = models.DateField()
    voucher = models.ForeignKey(Voucher, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='voucher_id')
    purpose = models.CharField(max_length=500)
    category = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    given_to = models.CharField(max_length=150, blank=True, null=True)
    received_from = models.CharField(max_length=150, blank=True, null=True)
    receipt_attached = models.BooleanField(default=False)
    running_balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='approved_by')
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='created_by', related_name='created_petty_cash'
    )

    class Meta:
        db_table = 'petty_cash'
        ordering = ['-date']


class LateFeeCharge(models.Model):
    charge_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('students.Student', on_delete=models.DO_NOTHING, db_column='student_id')
    due = models.ForeignKey('students.StudentDue', on_delete=models.DO_NOTHING, db_column='due_id')
    charge_date = models.DateField()
    days_overdue = models.IntegerField()
    base_amount = models.DecimalField(max_digits=15, decimal_places=2)
    late_fee_rate = models.DecimalField(max_digits=5, decimal_places=2)
    late_fee_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=9, default='Calculated')
    voucher = models.ForeignKey(Voucher, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='voucher_id')
    approved_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='approved_by', related_name='approved_late_fees'
    )
    waived_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='waived_by'
    )
    waive_reason = models.TextField(blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'late_fee_charges'


class FinancialSnapshot(models.Model):
    snapshot_id = models.AutoField(primary_key=True)
    snapshot_date = models.DateField()
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column='branch_id')
    total_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_equity = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    bank_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    receivable_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    payable_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_students = models.IntegerField(default=0)
    active_students = models.IntegerField(default=0)
    new_admissions = models.IntegerField(default=0)
    total_collections = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    snapshot_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'financial_snapshots'
        unique_together = [('snapshot_date', 'branch')]
        ordering = ['-snapshot_date']
