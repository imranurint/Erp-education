from rest_framework import serializers
from .models import (
    Department, Designation, Employee, SalaryStructure,
    LeaveType, LeaveRequest, LeaveBalance, StaffAttendance,
    Payroll, PayrollItem, TeacherAssignment, CounselorAssignment,
    StudentMeeting
)


class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head_user.name', read_only=True, default=None)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True, default=None)

    class Meta:
        model = Department
        fields = '__all__'


class DesignationSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source='department.department_name', read_only=True, default=None
    )

    class Meta:
        model = Designation
        fields = '__all__'


class SalaryStructureSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.name', read_only=True)
    employee_code = serializers.CharField(source='employee.employee_code', read_only=True)

    class Meta:
        model = SalaryStructure
        fields = '__all__'


class EmployeeListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    department_name = serializers.CharField(
        source='department.department_name', read_only=True, default=None
    )
    designation_name = serializers.CharField(
        source='designation.designation_name', read_only=True, default=None
    )
    branch_name = serializers.CharField(
        source='branch.branch_name', read_only=True, default=None
    )

    class Meta:
        model = Employee
        fields = [
            'employee_id', 'employee_code', 'user', 'user_name', 'user_email',
            'user_role', 'department', 'department_name', 'designation',
            'designation_name', 'employment_type', 'date_of_joining',
            'qualification', 'status', 'branch', 'branch_name',
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    department_name = serializers.CharField(
        source='department.department_name', read_only=True, default=None
    )
    designation_name = serializers.CharField(
        source='designation.designation_name', read_only=True, default=None
    )
    branch_name = serializers.CharField(
        source='branch.branch_name', read_only=True, default=None
    )
    current_salary = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    def get_current_salary(self, obj):
        salary = SalaryStructure.objects.filter(employee=obj, is_current=True).first()
        if salary:
            return {
                'basic': str(salary.basic_salary),
                'gross': str(salary.gross_salary),
                'net': str(salary.net_salary),
            }
        return None


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.name', read_only=True)
    employee_code = serializers.CharField(source='employee.employee_code', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.type_name', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = '__all__'


class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.type_name', read_only=True)

    class Meta:
        model = LeaveBalance
        fields = '__all__'


class StaffAttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.name', read_only=True)
    employee_code = serializers.CharField(source='employee.employee_code', read_only=True)

    class Meta:
        model = StaffAttendance
        fields = '__all__'


class PayrollItemSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.name', read_only=True)
    employee_code = serializers.CharField(source='employee.employee_code', read_only=True)

    class Meta:
        model = PayrollItem
        fields = '__all__'


class PayrollListSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True, default=None)

    class Meta:
        model = Payroll
        exclude = ['created_by', 'approved_by']


class PayrollDetailSerializer(serializers.ModelSerializer):
    items = PayrollItemSerializer(many=True, read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True, default=None)

    class Meta:
        model = Payroll
        fields = '__all__'


class TeacherAssignmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.name', read_only=True)
    programme_name = serializers.CharField(source='programme.programme_name', read_only=True)

    class Meta:
        model = TeacherAssignment
        fields = '__all__'


class CounselorAssignmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.name', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_code = serializers.CharField(source='student.student_code', read_only=True)

    class Meta:
        model = CounselorAssignment
        fields = '__all__'


class StudentMeetingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    counselor_name = serializers.CharField(source='employee.user.name', read_only=True)

    class Meta:
        model = StudentMeeting
        fields = '__all__'