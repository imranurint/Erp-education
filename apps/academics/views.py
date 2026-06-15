from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.permissions import BranchIsolationMixin, IsAccountantOrAbove
from .models import Programme, AcademicYear, FiscalPeriod, AcademicRecord, Attendance
from .serializers import (
    ProgrammeSerializer, AcademicYearSerializer, FiscalPeriodSerializer,
    AcademicRecordSerializer, AttendanceSerializer, BulkAttendanceSerializer
)


class ProgrammeViewSet(BranchIsolationMixin, viewsets.ModelViewSet):
    queryset = Programme.objects.all()
    serializer_class = ProgrammeSerializer
    filterset_fields = ['status', 'code', 'branch']
    search_fields = ['programme_name', 'code']


class AcademicYearViewSet(BranchIsolationMixin, viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    filterset_fields = ['status', 'branch']

    @action(detail=True, methods=['post'])
    def close_year(self, request, pk=None):
        year = self.get_object()
        year.status = 'Closed'
        year.save(update_fields=['status'])
        return Response({'message': f'{year.year_name} closed'})

    @action(detail=True, methods=['post'])
    def generate_periods(self, request, pk=None):
        """Auto-generate 12 monthly fiscal periods for this year."""
        year = self.get_object()
        import calendar
        from datetime import date

        periods = []
        for month in range(1, 13):
            start = date(year.start_date.year if month >= year.start_date.month
                         else year.end_date.year, month, 1)
            last_day = calendar.monthrange(start.year, start.month)[1]
            end = date(start.year, start.month, last_day)

            period, _ = FiscalPeriod.objects.get_or_create(
                year=year, period_number=month, branch=year.branch,
                defaults={
                    'period_name': start.strftime('%B %Y'),
                    'start_date': start,
                    'end_date': end,
                }
            )
            periods.append(FiscalPeriodSerializer(period).data)

        return Response(periods)


class FiscalPeriodViewSet(viewsets.ModelViewSet):
    queryset = FiscalPeriod.objects.select_related('year').all()
    serializer_class = FiscalPeriodSerializer
    filterset_fields = ['year', 'is_closed', 'branch']

    @action(detail=True, methods=['post'])
    def close_period(self, request, pk=None):
        period = self.get_object()
        period.is_closed = True
        period.closed_by = request.user
        period.save(update_fields=['is_closed', 'closed_by'])
        return Response({'message': f'{period.period_name} closed'})


class AcademicRecordViewSet(viewsets.ModelViewSet):
    queryset = AcademicRecord.objects.select_related(
        'student', 'programme'
    ).all()
    serializer_class = AcademicRecordSerializer
    filterset_fields = ['student', 'programme', 'result', 'assessment_type', 'branch']
    search_fields = ['module_name', 'module_code', 'student__full_name']


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('student').all()
    serializer_class = AttendanceSerializer
    filterset_fields = ['student', 'programme', 'attendance_date', 'status', 'branch']

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Mark attendance for multiple students at once."""
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        created = []
        for record in data['records']:
            att, _ = Attendance.objects.update_or_create(
                student_id=record['student_id'],
                attendance_date=data['attendance_date'],
                session_type=data['session_type'],
                defaults={
                    'programme_id': data['programme_id'],
                    'status': record['status'],
                    'time_in': record.get('time_in'),
                    'recorded_by': request.user,
                    'branch': request.user.branch,
                }
            )
            created.append(AttendanceSerializer(att).data)

        return Response(created, status=status.HTTP_201_CREATED)
