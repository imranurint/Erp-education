from django.db import models
from apps.core.models import Branch


class Programme(models.Model):
    programme_id = models.AutoField(primary_key=True)
    programme_name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    duration_months = models.IntegerField(blank=True, null=True)
    total_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='BDT')
    description = models.TextField(blank=True, null=True)
    ncuK_programme_code = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=8,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive')],
        default='Active'
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='branch_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'programmes'
        managed = False
        ordering = ['programme_name']

    def __str__(self):
        return f"{self.code} - {self.programme_name}"


class AcademicYear(models.Model):
    year_id = models.AutoField(primary_key=True)
    year_name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=6,
        choices=[('Active', 'Active'), ('Closed', 'Closed')],
        default='Active'
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='branch_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'academic_years'
        managed = False
        ordering = ['-start_date']

    def __str__(self):
        return self.year_name


class FiscalPeriod(models.Model):
    period_id = models.AutoField(primary_key=True)
    year = models.ForeignKey(
        AcademicYear, on_delete=models.DO_NOTHING, db_column='year_id'
    )
    period_name = models.CharField(max_length=30)
    period_number = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)
    closed_by = models.ForeignKey(
        'core.User', on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='closed_by'
    )
    closed_date = models.DateTimeField(blank=True, null=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='branch_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fiscal_periods'
        managed = False
        unique_together = [('year', 'period_number', 'branch')]
        ordering = ['year', 'period_number']


class AcademicRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        'students.Student', on_delete=models.DO_NOTHING, db_column='student_id'
    )
    programme = models.ForeignKey(
        Programme, on_delete=models.DO_NOTHING, db_column='programme_id'
    )
    module_name = models.CharField(max_length=200)
    module_code = models.CharField(max_length=20, blank=True, null=True)
    assessment_type = models.CharField(max_length=15)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    grade = models.CharField(max_length=10, blank=True, null=True)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    result = models.CharField(max_length=10, default='Pending')
    assessment_date = models.DateField(blank=True, null=True)
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='academic_year_id'
    )
    remarks = models.CharField(max_length=500, blank=True, null=True)
    recorded_by = models.ForeignKey(
        'core.User', on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='recorded_by'
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='branch_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'academic_records'
        managed = False


class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        'students.Student', on_delete=models.DO_NOTHING, db_column='student_id'
    )
    programme = models.ForeignKey(
        Programme, on_delete=models.DO_NOTHING, db_column='programme_id'
    )
    attendance_date = models.DateField()
    session_type = models.CharField(max_length=10, default='Lecture')
    status = models.CharField(max_length=7)
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    remarks = models.CharField(max_length=300, blank=True, null=True)
    recorded_by = models.ForeignKey(
        'core.User', on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='recorded_by'
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.DO_NOTHING, blank=True, null=True,
        db_column='branch_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance'
        managed = False
        unique_together = [('student', 'attendance_date', 'session_type')]
