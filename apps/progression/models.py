from django.db import models
from apps.core.models import Branch, User


class ProgressionRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('students.Student', on_delete=models.DO_NOTHING, db_column='student_id')
    university = models.ForeignKey('partners.University', on_delete=models.DO_NOTHING, db_column='university_id')
    programme_applied = models.CharField(max_length=300, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # Application
    application_date = models.DateField(blank=True, null=True)
    application_status = models.CharField(max_length=20, default='Not Started')

    # Offer
    offer_date = models.DateField(blank=True, null=True)
    offer_type = models.CharField(max_length=12, blank=True, null=True)
    offer_conditions = models.TextField(blank=True, null=True)
    offer_letter_path = models.CharField(max_length=500, blank=True, null=True)
    tuition_fee_at_uni = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    tuition_currency = models.CharField(max_length=3, default='GBP')
    scholarship_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    scholarship_details = models.CharField(max_length=300, blank=True, null=True)

    # Visa
    visa_status = models.CharField(max_length=15, default='Not Started')
    visa_application_date = models.DateField(blank=True, null=True)
    visa_grant_date = models.DateField(blank=True, null=True)
    visa_number = models.CharField(max_length=50, blank=True, null=True)
    visa_document_path = models.CharField(max_length=500, blank=True, null=True)

    # Enrollment
    enrollment_status = models.CharField(max_length=12, default='Not Enrolled')
    enrollment_date = models.DateField(blank=True, null=True)
    enrollment_confirmation_path = models.CharField(max_length=500, blank=True, null=True)

    # Commission
    commission_status = models.CharField(max_length=15, default='Not Applicable')

    notes = models.TextField(blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='created_by')

    class Meta:
        db_table = 'progression_records'
        managed = False
        ordering = ['-created_at']


class UniversityCommission(models.Model):
    commission_id = models.AutoField(primary_key=True)
    progression_record = models.ForeignKey(ProgressionRecord, on_delete=models.DO_NOTHING, db_column='progression_record_id')
    university = models.ForeignKey('partners.University', on_delete=models.DO_NOTHING, db_column='university_id')
    student = models.ForeignKey('students.Student', on_delete=models.DO_NOTHING, db_column='student_id')
    commission_type = models.CharField(max_length=25)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    tuition_base = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    gross_commission = models.DecimalField(max_digits=15, decimal_places=2)
    commission_currency = models.CharField(max_length=3, default='GBP')
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)
    commission_in_bdt = models.DecimalField(max_digits=15, decimal_places=2)
    expected_date = models.DateField(blank=True, null=True)
    received_date = models.DateField(blank=True, null=True)
    received_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    received_currency = models.CharField(max_length=3, blank=True, null=True)
    received_exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True)
    received_amount_bdt = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_ref = models.CharField(max_length=100, blank=True, null=True)
    bank_coa = models.ForeignKey('accounting.ChartOfAccount', on_delete=models.DO_NOTHING, blank=True, null=True, db_column='bank_coa_id')
    status = models.CharField(max_length=12, default='Expected')
    voucher = models.ForeignKey('accounting.Voucher', on_delete=models.DO_NOTHING, blank=True, null=True, db_column='voucher_id')
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    invoice_path = models.CharField(max_length=500, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='created_by')

    class Meta:
        db_table = 'university_commissions'
        managed = False


class PartnerCommission(models.Model):
    partner_commission_id = models.AutoField(primary_key=True)
    partner = models.ForeignKey('partners.Partner', on_delete=models.DO_NOTHING, db_column='partner_id')
    student = models.ForeignKey('students.Student', on_delete=models.DO_NOTHING, db_column='student_id')
    university_commission = models.ForeignKey(UniversityCommission, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='university_commission_id')
    commission_type = models.CharField(max_length=40)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    base_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    calculated_amount = models.DecimalField(max_digits=15, decimal_places=2)
    calculated_date = models.DateField()
    approved_by = models.ForeignKey(
    User,
    on_delete=models.DO_NOTHING,
    blank=True,
    null=True,
    db_column='approved_by',
    related_name='approved_commissions'  # Unique name for reverse accessor
)
    approval_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=15, default='Calculated')
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2)
    voucher = models.ForeignKey('accounting.Voucher', on_delete=models.DO_NOTHING, blank=True, null=True, db_column='voucher_id')
    notes = models.TextField(blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
    User,
    on_delete=models.DO_NOTHING,
    blank=True,
    null=True,
    db_column='created_by',
    related_name='created_commissions'  # Unique name for reverse accessor
)

    class Meta:
        db_table = 'partner_commissions'
        managed = False


class PartnerPayment(models.Model):
    partner_payment_id = models.AutoField(primary_key=True)
    partner_commission = models.ForeignKey(PartnerCommission, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='partner_commission_id')
    partner = models.ForeignKey('partners.Partner', on_delete=models.DO_NOTHING, db_column='partner_id')
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    payment_method = models.CharField(max_length=15)
    transaction_ref = models.CharField(max_length=100, blank=True, null=True)
    bank_coa = models.ForeignKey('accounting.ChartOfAccount', on_delete=models.DO_NOTHING, blank=True, null=True, db_column='bank_coa_id')
    voucher = models.ForeignKey('accounting.Voucher', on_delete=models.DO_NOTHING, blank=True, null=True, db_column='voucher_id')
    batch_reference = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=10, default='Pending')
    notes = models.TextField(blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='created_by')
    approved_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='approved_by', related_name='approved_partner_payments')

    class Meta:
        db_table = 'partner_payments'
        managed = False
