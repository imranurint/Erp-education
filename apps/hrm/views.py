from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Department, Designation, Employee, SalaryStructure,
    LeaveType, LeaveRequest, LeaveBalance, StaffAttendance,
    Payroll, PayrollItem, TeacherAssignment, CounselorAssignment,
    StudentMeeting
)
from .serializers import (
    DepartmentSerializer, DesignationSerializer,
    EmployeeListSerializer, EmployeeDetailSerializer,
    SalaryStructureSerializer, LeaveTypeSerializer,
    LeaveRequestSerializer, LeaveBalanceSerializer,
    StaffAttendanceSerializer, PayrollListSerializer,
    PayrollDetailSerializer, PayrollItemSerializer,
    TeacherAssignmentSerializer, CounselorAssignmentSerializer,
    StudentMeetingSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related('head_user', 'branch').all()
    serializer_class = DepartmentSerializer
    filterset_fields = ['status', 'branch']
    search_fields = ['department_name']


class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.select_related('department').all()
    serializer_class = DesignationSerializer
    filterset_fields = ['department', 'status']


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related(
        'user', 'department', 'designation', 'branch'
    ).all()
    filterset_fields = [
        'status', 'department', 'designation', 'employment_type', 'branch', 'gender'
    ]
    search_fields = ['employee_code', 'user__name', 'user__email', 'qualification']
    ordering_fields = ['employee_code', 'date_of_joining', 'user__name']

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeDetailSerializer

    @action(detail=True, methods=['get'])
    def salary(self, request, pk=None):
        emp = self.get_object()
        salaries = SalaryStructure.objects.filter(employee=emp).order_by('-effective_from')
        return Response(SalaryStructureSerializer(salaries, many=True).data)

    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        emp = self.get_object()
        qs = StaffAttendance.objects.filter(employee=emp)
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        if month and year:
            qs = qs.filter(attendance_date__month=month, attendance_date__year=year)
        return Response(
            StaffAttendanceSerializer(qs.order_by('-attendance_date'), many=True).data
        )

    @action(detail=True, methods=['get'])
    def leaves(self, request, pk=None):
        emp = self.get_object()
        qs = LeaveRequest.objects.filter(employee=emp).order_by('-created_at')
        return Response(LeaveRequestSerializer(qs, many=True).data)

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Students assigned to this employee (as counselor)."""
        emp = self.get_object()
        qs = CounselorAssignment.objects.filter(
            employee=emp, status='Active'
        ).select_related('student')
        return Response(CounselorAssignmentSerializer(qs, many=True).data)

    @action(detail=True, methods=['get'])
    def teaching(self, request, pk=None):
        """Teaching assignments for this employee."""
        emp = self.get_object()
        qs = TeacherAssignment.objects.filter(
            employee=emp
        ).select_related('programme')
        return Response(TeacherAssignmentSerializer(qs, many=True).data)


class SalaryStructureViewSet(viewsets.ModelViewSet):
    queryset = SalaryStructure.objects.select_related('employee__user').all()
    serializer_class = SalaryStructureSerializer
    filterset_fields = ['employee', 'is_current']


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related(
        'employee__user', 'leave_type'
    ).all()
    serializer_class = LeaveRequestSerializer
    filterset_fields = ['status', 'employee', 'leave_type', 'branch']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'Approved'
        leave.approved_by = request.user
        leave.save(update_fields=['status', 'approved_by'])
        # Update balance
        balance = LeaveBalance.objects.filter(
            employee=leave.employee, leave_type=leave.leave_type,
            year=leave.start_date.year
        ).first()
        if balance:
            balance.taken += leave.total_days
            balance.remaining -= leave.total_days
            balance.save(update_fields=['taken', 'remaining'])
        return Response(LeaveRequestSerializer(leave).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'Rejected'
        leave.approved_by = request.user
        leave.rejection_reason = request.data.get('reason', '')
        leave.save(update_fields=['status', 'approved_by', 'rejection_reason'])
        return Response(LeaveRequestSerializer(leave).data)


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.select_related(
        'employee__user', 'leave_type'
    ).all()
    serializer_class = LeaveBalanceSerializer
    filterset_fields = ['employee', 'leave_type', 'year']


class StaffAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StaffAttendance.objects.select_related('employee__user').all()
    serializer_class = StaffAttendanceSerializer
    filterset_fields = ['employee', 'status', 'attendance_date', 'branch']

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk mark attendance: POST {records: [{employee_id, attendance_date, status, ...}]}"""
        records = request.data.get('records', [])
        created = []
        for rec in records:
            att, _ = StaffAttendance.objects.update_or_create(
                employee_id=rec['employee_id'],
                attendance_date=rec['attendance_date'],
                defaults={
                    'status': rec['status'],
                    'time_in': rec.get('time_in'),
                    'time_out': rec.get('time_out'),
                    'overtime_hours': rec.get('overtime_hours', 0),
                    'branch_id': rec.get('branch_id'),
                }
            )
            created.append(StaffAttendanceSerializer(att).data)
        return Response(created, status=status.HTTP_201_CREATED)


class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.select_related('branch').all()
    filterset_fields = ['status', 'payroll_month', 'payroll_year', 'branch']

    def get_serializer_class(self):
        if self.action == 'list':
            return PayrollListSerializer
        return PayrollDetailSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate payroll for a month.
        POST {"month": 6, "year": 2026, "branch_id": 1}
        """
        month = int(request.data.get('month'))
        year = int(request.data.get('year'))
        branch_id = request.data.get('branch_id')

        import calendar
        period_label = f"{calendar.month_name[month]} {year}"
        working_days = 26

        payroll = Payroll.objects.create(
            payroll_month=month, payroll_year=year,
            period_label=period_label,
            branch_id=branch_id, created_by=request.user,
        )

        employees = Employee.objects.filter(status='Active')
        if branch_id:
            employees = employees.filter(branch_id=branch_id)

        gross_total = 0
        deduction_total = 0
        net_total = 0

        for emp in employees:
            salary = SalaryStructure.objects.filter(employee=emp, is_current=True).first()
            if not salary:
                continue

            absent_days = StaffAttendance.objects.filter(
                employee=emp, attendance_date__month=month,
                attendance_date__year=year, status='Absent'
            ).count()

            total_overtime = sum(
                float(h) for h in StaffAttendance.objects.filter(
                    employee=emp, attendance_date__month=month,
                    attendance_date__year=year
                ).values_list('overtime_hours', flat=True)
            )

            absent_ded = round(float(salary.basic_salary) / working_days * absent_days)
            overtime_pay = round(
                float(salary.basic_salary) / working_days / 8 * total_overtime * 1.5
            )
            gross = float(salary.gross_salary) + overtime_pay
            total_ded = float(salary.total_deduction) + absent_ded
            net = gross - total_ded

            PayrollItem.objects.create(
                payroll=payroll, employee=emp,
                basic_salary=salary.basic_salary,
                house_rent=salary.house_rent,
                medical_allowance=salary.medical_allowance,
                transport_allowance=salary.transport_allowance,
                food_allowance=salary.food_allowance,
                mobile_allowance=salary.mobile_allowance,
                other_allowance=salary.other_allowance,
                overtime_amount=overtime_pay,
                gross_salary=gross,
                provident_fund=salary.provident_fund,
                tax_deduction=salary.tax_deduction,
                insurance_deduction=salary.insurance_deduction,
                absent_deduction=absent_ded,
                total_deduction=total_ded,
                net_salary=net,
                days_worked=working_days - absent_days,
                days_absent=absent_days,
                overtime_hours=total_overtime,
                branch_id=branch_id or emp.branch_id,
            )

            gross_total += gross
            deduction_total += total_ded
            net_total += net

        payroll.total_employees = employees.count()
        payroll.gross_total = gross_total
        payroll.deduction_total = deduction_total
        payroll.net_total = net_total
        payroll.status = 'Processing'
        payroll.save()

        return Response(PayrollDetailSerializer(payroll).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        payroll = self.get_object()
        payroll.status = 'Approved'
        payroll.approved_by = request.user
        payroll.save(update_fields=['status', 'approved_by', 'updated_at'])
        return Response(PayrollDetailSerializer(payroll).data)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        payroll = self.get_object()
        payroll.status = 'Paid'
        payroll.paid_date = request.data.get('paid_date')
        payroll.save(update_fields=['status', 'paid_date', 'updated_at'])
        PayrollItem.objects.filter(payroll=payroll).update(
            status='Paid', paid_date=payroll.paid_date
        )
        return Response(PayrollDetailSerializer(payroll).data)

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        payroll = self.get_object()
        items = PayrollItem.objects.filter(payroll=payroll).select_related('employee__user')
        return Response(PayrollItemSerializer(items, many=True).data)


class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TeacherAssignment.objects.select_related(
        'employee__user', 'programme', 'academic_year'
    ).all()
    serializer_class = TeacherAssignmentSerializer
    filterset_fields = ['employee', 'programme', 'academic_year', 'status', 'branch']
    search_fields = ['module_name', 'module_code', 'employee__user__name']


class CounselorAssignmentViewSet(viewsets.ModelViewSet):
    queryset = CounselorAssignment.objects.select_related(
        'employee__user', 'student'
    ).all()
    serializer_class = CounselorAssignmentSerializer
    filterset_fields = ['employee', 'student', 'assignment_type', 'status', 'branch']
    search_fields = ['student__full_name', 'student__student_code', 'employee__user__name']


class StudentMeetingViewSet(viewsets.ModelViewSet):
    queryset = StudentMeeting.objects.select_related(
        'student', 'employee__user'
    ).all()
    serializer_class = StudentMeetingSerializer
    filterset_fields = ['student', 'employee', 'meeting_type', 'branch']
    search_fields = ['student__full_name', 'purpose', 'discussion']
    ordering_fields = ['meeting_date']