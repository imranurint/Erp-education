from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from apps.core.permissions import BranchIsolationMixin, IsCollectorOrAbove
from .models import Student, StudentDocument, StudentFeeSetup, StudentDue, Discount
from .serializers import (
    StudentListSerializer, StudentDetailSerializer, StudentCreateSerializer,
    StudentDocumentSerializer, StudentFeeSetupSerializer,
    StudentDueSerializer, DiscountSerializer
)


class StudentViewSet(BranchIsolationMixin, viewsets.ModelViewSet):
    queryset = Student.objects.select_related('programme', 'branch', 'partner').all()
    filterset_fields = [
        'status', 'progression_status', 'programme', 'branch',
        'partner', 'referral_source', 'admission_date',
    ]
    search_fields = ['full_name', 'student_code', 'contact_no', 'email', 'passport_no']
    ordering_fields = ['full_name', 'admission_date', 'total_due', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return StudentCreateSerializer
        if self.action == 'list':
            return StudentListSerializer
        return StudentDetailSerializer

    @action(detail=True, methods=['get'])
    def ledger(self, request, pk=None):
        """Get student ledger (statement of account)."""
        from apps.accounting.models import StudentLedger
        student = self.get_object()
        entries = StudentLedger.objects.filter(student=student).order_by('entry_date')
        from apps.accounting.serializers import StudentLedgerSerializer
        return Response(StudentLedgerSerializer(entries, many=True).data)

    @action(detail=True, methods=['get'])
    def dues(self, request, pk=None):
        """Get student's fee dues."""
        student = self.get_object()
        dues = StudentDue.objects.filter(student=student).select_related('coa')
        serializer = StudentDueSerializer(dues, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """List all students with overdue payments."""
        students = self.get_queryset().filter(
            studentdue__status='Overdue',
            status='Active'
        ).distinct()
        serializer = StudentListSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Financial summary of all students."""
        qs = self.get_queryset().filter(status='Active')
        data = qs.aggregate(
            total_students=qs.count(),
            total_fee=Sum('total_fee'),
            total_paid=Sum('total_paid'),
            total_due=Sum('total_due'),
        )
        return Response(data)


class StudentDocumentViewSet(viewsets.ModelViewSet):
    queryset = StudentDocument.objects.select_related('student').all()
    serializer_class = StudentDocumentSerializer
    filterset_fields = ['student', 'document_type', 'is_verified']


class StudentFeeSetupViewSet(viewsets.ModelViewSet):
    queryset = StudentFeeSetup.objects.select_related('student', 'programme').all()
    serializer_class = StudentFeeSetupSerializer
    filterset_fields = ['student', 'programme', 'branch']

    @action(detail=True, methods=['post'])
    def generate_dues(self, request, pk=None):
        """Auto-generate student dues from fee setup."""
        setup = self.get_object()
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.callproc('sp_generate_student_dues', [setup.student_id, setup.setup_id])
        dues = StudentDue.objects.filter(student=setup.student)
        return Response(StudentDueSerializer(dues, many=True).data)


class StudentDueViewSet(viewsets.ModelViewSet):
    queryset = StudentDue.objects.select_related('student', 'coa').all()
    serializer_class = StudentDueSerializer
    filterset_fields = ['student', 'status', 'coa', 'due_date', 'branch']
    ordering_fields = ['due_date', 'amount', 'due_amount']

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.now().date()
        due_soon = self.get_queryset().filter(
            due_date__range=[today, today + timedelta(days=30)],
            status__in=['Unpaid', 'Partial']
        )
        return Response(StudentDueSerializer(due_soon, many=True).data)


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.select_related('student').all()
    serializer_class = DiscountSerializer
    filterset_fields = ['student', 'discount_type', 'branch']
