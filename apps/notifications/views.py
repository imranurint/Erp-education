import os
from django.http import FileResponse
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import EmailQueue, GeneratedDocument, ScheduledTaskLog
from .serializers import (
    EmailQueueSerializer, GeneratedDocumentSerializer,
    ScheduledTaskLogSerializer
)
from .pdf_service import (
    generate_receipt_pdf, generate_payslip_pdf,
    generate_income_statement_pdf, generate_balance_sheet_pdf,
    generate_student_statement_pdf, generate_invoice_pdf
)


class EmailQueueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailQueue.objects.all()
    serializer_class = EmailQueueSerializer
    filterset_fields = ['status', 'priority', 'reference_type']
    ordering_fields = ['created_at']


class GeneratedDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GeneratedDocument.objects.all()
    serializer_class = GeneratedDocumentSerializer
    filterset_fields = ['document_type', 'generated_for']
    ordering_fields = ['created_at']


class ScheduledTaskLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScheduledTaskLog.objects.all()
    serializer_class = ScheduledTaskLogSerializer
    ordering_fields = ['started_at']


# ── PDF Download Endpoints ───────────────────────────────

@api_view(['GET'])
def download_receipt(request, payment_id):
    """GET /api/v1/documents/receipt/{payment_id}/"""
    from apps.accounting.models import Payment
    try:
        payment = Payment.objects.select_related(
            'student', 'branch'
        ).get(pk=payment_id)
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=404)

    filepath, filename = generate_receipt_pdf(payment)

    # Record in generated_documents
    GeneratedDocument.objects.create(
        document_type='Receipt',
        reference_type='Payment',
        reference_id=payment_id,
        file_name=filename,
        file_path=filepath,
        file_size=os.path.getsize(filepath),
        generated_for=payment.student_id,
        generated_by=request.user if request.user.is_authenticated else None,
        branch=payment.branch,
    )

    return FileResponse(
        open(filepath, 'rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=filename,
    )


@api_view(['GET'])
def download_payslip(request, payroll_item_id):
    """GET /api/v1/documents/payslip/{payroll_item_id}/"""
    from apps.hrm.models import PayrollItem
    try:
        item = PayrollItem.objects.select_related(
            'employee__user', 'employee__department',
            'employee__designation', 'payroll'
        ).get(pk=payroll_item_id)
    except PayrollItem.DoesNotExist:
        return Response({'error': 'Payroll item not found'}, status=404)

    filepath, filename = generate_payslip_pdf(item, item.payroll)

    GeneratedDocument.objects.create(
        document_type='Payslip',
        reference_type='PayrollItem',
        reference_id=payroll_item_id,
        file_name=filename,
        file_path=filepath,
        file_size=os.path.getsize(filepath),
        generated_for=item.employee_id,
        generated_by=request.user if request.user.is_authenticated else None,
        branch=item.branch,
    )

    return FileResponse(
        open(filepath, 'rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=filename,
    )


@api_view(['POST'])
def download_income_statement(request):
    """
    POST /api/v1/documents/income-statement/
    Body: {"start_date": "2025-10-01", "end_date": "2026-06-30", "branch_id": 1}
    """
    start = request.data.get('start_date')
    end = request.data.get('end_date')
    branch_id = request.data.get('branch_id')

    if not start or not end:
        return Response(
            {'error': 'start_date and end_date required'},
            status=400
        )

    filepath, filename = generate_income_statement_pdf(start, end, branch_id)

    GeneratedDocument.objects.create(
        document_type='Income Statement',
        file_name=filename,
        file_path=filepath,
        file_size=os.path.getsize(filepath),
        generated_by=request.user if request.user.is_authenticated else None,
        branch_id=branch_id,
    )

    return FileResponse(
        open(filepath, 'rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=filename,
    )


@api_view(['POST'])
def download_balance_sheet(request):
    """
    POST /api/v1/documents/balance-sheet/
    Body: {"as_of_date": "2026-06-30", "branch_id": 1}
    """
    as_of = request.data.get('as_of_date')
    branch_id = request.data.get('branch_id')

    if not as_of:
        return Response({'error': 'as_of_date required'}, status=400)

    filepath, filename = generate_balance_sheet_pdf(as_of, branch_id)

    GeneratedDocument.objects.create(
        document_type='Balance Sheet',
        file_name=filename,
        file_path=filepath,
        file_size=os.path.getsize(filepath),
        generated_by=request.user if request.user.is_authenticated else None,
        branch_id=branch_id,
    )

    return FileResponse(
        open(filepath, 'rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=filename,
    )


@api_view(['GET'])
def download_student_statement(request, student_id):
    """GET /api/v1/documents/student-statement/{student_id}/"""
    from apps.students.models import Student
    try:
        student = Student.objects.select_related('programme', 'branch').get(pk=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)

    filepath, filename = generate_student_statement_pdf(student)

    GeneratedDocument.objects.create(
        document_type='Student Statement',
        reference_type='Student',
        reference_id=student_id,
        file_name=filename,
        file_path=filepath,
        file_size=os.path.getsize(filepath),
        generated_for=student_id,
        generated_by=request.user if request.user.is_authenticated else None,
        branch=student.branch,
    )

    return FileResponse(
        open(filepath, 'rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=filename,
    )


@api_view(['GET'])
def download_invoice(request, student_id):
    """GET /api/v1/documents/invoice/{student_id}/"""
    from apps.students.models import Student
    try:
        student = Student.objects.select_related('programme', 'branch').get(pk=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)

    filepath, filename = generate_invoice_pdf(student)

    GeneratedDocument.objects.create(
        document_type='Invoice',
        reference_type='Student',
        reference_id=student_id,
        file_name=filename,
        file_path=filepath,
        file_size=os.path.getsize(filepath),
        generated_for=student_id,
        generated_by=request.user if request.user.is_authenticated else None,
        branch=student.branch,
    )

    return FileResponse(
        open(filepath, 'rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=filename,
    )