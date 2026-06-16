from django.db import models
from apps.core.models import Branch, User
from apps.academics.models import Programme


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    student_code = models.CharField(max_length=30, unique=True)

    # Personal
    full_name = models.CharField(max_length=200)
    father_name = models.CharField(max_length=150, blank=True, null=True)
    mother_name = models.CharField(max_length=150, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=6, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    nationality = models.CharField(max_length=50, default='Bangladeshi')

    # Identification
    national_id = models.CharField(max_length=30, blank=True, null=True)
    passport_no = models.CharField(max_length=30, blank=True, null=True)
    passport_expiry = models.DateField(blank=True, null=True)

    # Contact
    contact_no = models.CharField(max_length=30, blank=True, null=True)
    alternate_contact_no = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    present_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)

    # Emergency
    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True, null=True)

    # Academic
    education_qualification = models.CharField(max_length=100, blank=True, null=True)
    institution_name = models.CharField(max_length=200, blank=True, null=True)
    gpa_or_grade = models.CharField(max_length=20, blank=True, null=True)
    english_proficiency = models.CharField(max_length=50, blank=True, null=True)
    english_score = models.CharField(max_length=20, blank=True, null=True)

    # Admission
    admission_date = models.DateField()
    programme = models.ForeignKey(
        Programme, on_delete=models.DO_NOTHING, db_column='programme_id'
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.DO_NOTHING, db_column='branch_id'
    )
    ncuK_student_id = models.CharField(max_length=50, blank=True, null=True)
    photo_path = models.CharField(max_length=500, blank=True, null=True)

    # Partner
    partner = models.ForeignKey(
        'partners.Partner', on_delete=models.DO_NOTHING,
        blank=True, null=True, db_column='partner_id'
    )
    partner_ref_number = models.CharField(max_length=50, blank=True, null=True)

    # Referral
    referral_source = models.CharField(max_length=20, default='Walk-in')
    referred_by_student = models.ForeignKey(
        'self', on_delete=models.DO_NOTHING,
        blank=True, null=True, db_column='referred_by_student_id'
    )

    # Status
    status = models.CharField(max_length=12, default='Active')
    progression_status = models.CharField(max_length=20, default='Studying')

    # Financial summary (denormalized)
    total_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_due = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='created_by'
    )

    class Meta:
        db_table = 'students'
        ordering = ['-admission_date']

    def __str__(self):
        return f"{self.student_code} - {self.full_name}"


class StudentDocument(models.Model):
    doc_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, db_column='student_id')
    document_type = models.CharField(max_length=25)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField(blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='verified_by', related_name='verified_documents'
    )
    verified_date = models.DateTimeField(blank=True, null=True)
    notes = models.CharField(max_length=500, blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='branch_id')
    uploaded_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='uploaded_by', related_name='uploaded_documents'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_documents'


class StudentFeeSetup(models.Model):
    setup_id = models.AutoField(primary_key=True)
    student = models.OneToOneField(
        Student, on_delete=models.DO_NOTHING, db_column='student_id'
    )
    programme = models.ForeignKey(
        Programme, on_delete=models.DO_NOTHING, db_column='programme_id'
    )
    total_programme_fee = models.DecimalField(max_digits=15, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_type = models.CharField(max_length=10, blank=True, null=True)
    discount_reason = models.TextField(blank=True, null=True)
    discount_approved_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='discount_approved_by', related_name='approved_discounts'
    )
    net_payable = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    installment_count = models.IntegerField(default=1)
    first_installment_date = models.DateField(blank=True, null=True)
    next_interval_days = models.IntegerField(default=30)
    late_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    late_fee_max_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='approved_by', related_name='approved_fee_setups'
    )
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='created_by', related_name='created_fee_setups'
    )

    class Meta:
        db_table = 'student_fee_setup'


class StudentDue(models.Model):
    due_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, db_column='student_id')
    coa = models.ForeignKey(
        'accounting.ChartOfAccount', on_delete=models.DO_NOTHING, db_column='coa_id'
    )
    due_date = models.DateField()
    installment_no = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=15, decimal_places=2)
    late_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=8, default='Unpaid')
    academic_year = models.ForeignKey(
        'academics.AcademicYear', on_delete=models.DO_NOTHING,
        blank=True, null=True, db_column='academic_year_id'
    )
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_dues'
        ordering = ['due_date']


class Discount(models.Model):
    discount_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, db_column='student_id')
    discount_type = models.CharField(max_length=20)
    discount_basis = models.CharField(max_length=14)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    applicable_to = models.CharField(max_length=15, default='All Fees')
    applicable_coa = models.ForeignKey(
        'accounting.ChartOfAccount', on_delete=models.DO_NOTHING,
        blank=True, null=True, db_column='applicable_coa_id'
    )
    calculated_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reason = models.TextField()
    approved_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='approved_by')
    approval_date = models.DateField()
    valid_from = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='created_by', related_name='created_discounts'
    )

    class Meta:
        db_table = 'discounts'
