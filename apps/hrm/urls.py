from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, DesignationViewSet, EmployeeViewSet,
    SalaryStructureViewSet, LeaveTypeViewSet, LeaveRequestViewSet,
    LeaveBalanceViewSet, StaffAttendanceViewSet, PayrollViewSet,
    TeacherAssignmentViewSet, CounselorAssignmentViewSet,
    StudentMeetingViewSet
)

router = DefaultRouter()
router.register('departments', DepartmentViewSet)
router.register('designations', DesignationViewSet)
router.register('employees', EmployeeViewSet)
router.register('salary-structures', SalaryStructureViewSet)
router.register('leave-types', LeaveTypeViewSet)
router.register('leave-requests', LeaveRequestViewSet)
router.register('leave-balances', LeaveBalanceViewSet)
router.register('staff-attendance', StaffAttendanceViewSet)
router.register('payroll', PayrollViewSet)
router.register('teacher-assignments', TeacherAssignmentViewSet)
router.register('counselor-assignments', CounselorAssignmentViewSet)
router.register('student-meetings', StudentMeetingViewSet)

urlpatterns = [path('', include(router.urls))]