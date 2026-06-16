from django.db import models


class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    head_user = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='headed_departments'
    )
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=8, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        ordering = ['department_name']

    def __str__(self):
        return self.department_name


class Designation(models.Model):
    designation_id = models.AutoField(primary_key=True)
    designation_name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    level = models.IntegerField(default=1)
    status = models.CharField(max_length=8, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'designations'
        ordering = ['level', 'designation_name']

    def __str__(self):
        return self.designation_name


class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    user = models.OneToOneField('core.User', on_delete=models.CASCADE)
    employee_code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    designation = models.ForeignKey(
        Designation, on_delete=models.SET_NULL, null=True, blank=True
    )
    employment_type = models.CharField(
        max_length=15, default='Full-time',
        choices=[
            ('Full-time', 'Full-time'), ('Part-time', 'Part-time'),
            ('Contract', 'Contract'), ('Intern', 'Intern'), ('Visiting', 'Visiting'),
        ]
    )
    date_of_joining = models.DateField()
    date_of_leaving = models.DateField(null=True, blank=True)
    probation_end_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    qualification = models.CharField(max_length=200, blank=True, null=True)
    experience_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_no = models.CharField(max_length=50, blank=True, null=True)
    bank_branch = models.CharField(max_length=100, blank=True, null=True)
    tin_number = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact = models.CharField(max_length=150, blank=True, null=True)
    emergency_phone = models.CharField(max_length=30, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=6, blank=True, null=True,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    )
    marital_status = models.CharField(max_length=10, blank=True, null=True)
    present_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    photo_path = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(
        max_length=12, default='Active',
        choices=[
            ('Active', 'Active'), ('On Leave', 'On Leave'),
            ('Resigned', 'Resigned'), ('Terminated', 'Terminated'), ('Retired', 'Retired'),
        ]
    )
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        ordering = ['employee_code']

    def __str__(self):
        return f"{self.employee_code} - {self.user.name}"


class SalaryStructure(models.Model):
    structure_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=15, decimal_places=2)
    house_rent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    food_allowance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mobile_allowance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_allowance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=15, decimal_places=2)
    provident_fund = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    insurance_deduction = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_deduction = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deduction = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=15, decimal_places=2)
    effective_from = models.DateField()
    effective_until = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
    approved_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_salaries'
    )
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'salary_structures'
        ordering = ['-effective_from']


class LeaveType(models.Model):
    leave_type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=50)
    days_per_year = models.IntegerField()
    is_paid = models.BooleanField(default=True)
    carry_forward = models.BooleanField(default=False)
    status = models.CharField(max_length=8, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'leave_types'

    def __str__(self):
        return self.type_name


class LeaveRequest(models.Model):
    leave_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(max_digits=4, decimal_places=1)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=10, default='Pending',
        choices=[
            ('Pending', 'Pending'), ('Approved', 'Approved'),
            ('Rejected', 'Rejected'), ('Cancelled', 'Cancelled'),
        ]
    )
    approved_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_leaves'
    )
    approval_date = models.DateField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'leave_requests'
        ordering = ['-created_at']


class LeaveBalance(models.Model):
    balance_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.IntegerField()
    entitled = models.DecimalField(max_digits=4, decimal_places=1)
    taken = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    remaining = models.DecimalField(max_digits=4, decimal_places=1)
    carried_over = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'leave_balances'
        unique_together = [('employee', 'leave_type', 'year')]


class StaffAttendance(models.Model):
    staff_attendance_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('Present', 'Present'), ('Absent', 'Absent'), ('Late', 'Late'),
            ('Half Day', 'Half Day'), ('Leave', 'Leave'), ('Holiday', 'Holiday'),
        ]
    )
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    remarks = models.CharField(max_length=300, blank=True, null=True)
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'staff_attendance'
        unique_together = [('employee', 'attendance_date')]


class Payroll(models.Model):
    payroll_id = models.AutoField(primary_key=True)
    payroll_month = models.IntegerField()
    payroll_year = models.IntegerField()
    period_label = models.CharField(max_length=20)
    total_employees = models.IntegerField(default=0)
    gross_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    deduction_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    voucher = models.ForeignKey(
        'accounting.Voucher', on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=10, default='Draft',
        choices=[
            ('Draft', 'Draft'), ('Processing', 'Processing'),
            ('Approved', 'Approved'), ('Paid', 'Paid'), ('Cancelled', 'Cancelled'),
        ]
    )
    approved_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_payrolls'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_payrolls'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payroll'
        ordering = ['-payroll_year', '-payroll_month']
        unique_together = [('payroll_month', 'payroll_year', 'branch')]


class PayrollItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='items')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=15, decimal_places=2)
    house_rent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    food_allowance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mobile_allowance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_allowance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    overtime_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=15, decimal_places=2)
    provident_fund = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    insurance_deduction = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    advance_deduction = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    loan_deduction = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    absent_deduction = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_deduction = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deduction = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=15, decimal_places=2)
    days_worked = models.IntegerField(default=0)
    days_absent = models.IntegerField(default=0)
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    status = models.CharField(
        max_length=8, default='Pending',
        choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Hold', 'Hold')]
    )
    payment_method = models.CharField(max_length=20, blank=True, null=True)
    transaction_ref = models.CharField(max_length=100, blank=True, null=True)
    paid_date = models.DateField(null=True, blank=True)
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'payroll_items'


class TeacherAssignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    programme = models.ForeignKey('academics.Programme', on_delete=models.CASCADE)
    module_name = models.CharField(max_length=200)
    module_code = models.CharField(max_length=20, blank=True, null=True)
    academic_year = models.ForeignKey(
        'academics.AcademicYear', on_delete=models.SET_NULL, null=True, blank=True
    )
    hours_per_week = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    rate_per_hour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, default='Active')
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'teacher_assignments'


class CounselorAssignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    assigned_date = models.DateField()
    unassigned_date = models.DateField(null=True, blank=True)
    assignment_type = models.CharField(
        max_length=10, default='Primary',
        choices=[
            ('Primary', 'Primary'), ('Academic', 'Academic'),
            ('Career', 'Career'), ('Visa', 'Visa'),
        ]
    )
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=12, default='Active',
        choices=[
            ('Active', 'Active'), ('Completed', 'Completed'), ('Transferred', 'Transferred'),
        ]
    )
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'counselor_assignments'
        unique_together = [('employee', 'student', 'assignment_type')]


class StudentMeeting(models.Model):
    meeting_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    meeting_date = models.DateTimeField()
    meeting_type = models.CharField(
        max_length=10, default='In-person',
        choices=[
            ('In-person', 'In-person'), ('Phone', 'Phone'),
            ('Video', 'Video'), ('Email', 'Email'),
        ]
    )
    purpose = models.CharField(max_length=300, blank=True, null=True)
    discussion = models.TextField(blank=True, null=True)
    outcome = models.TextField(blank=True, null=True)
    next_meeting = models.DateField(null=True, blank=True)
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_meetings'
        ordering = ['-meeting_date']