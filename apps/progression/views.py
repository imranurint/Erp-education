from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import connection
from apps.core.permissions import BranchIsolationMixin, IsAccountantOrAbove
from .models import (
    ProgressionRecord, UniversityCommission,
    PartnerCommission, PartnerPayment
)
from .serializers import (
    ProgressionRecordSerializer, UniversityCommissionSerializer,
    PartnerCommissionSerializer, PartnerPaymentSerializer
)


class ProgressionRecordViewSet(BranchIsolationMixin, viewsets.ModelViewSet):
    queryset = ProgressionRecord.objects.select_related(
        'student', 'university'
    ).all()
    serializer_class = ProgressionRecordSerializer
    filterset_fields = [
        'application_status', 'visa_status', 'enrollment_status',
        'commission_status', 'university', 'student', 'branch',
    ]
    search_fields = ['student__full_name', 'university__university_name']

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update application/visa/enrollment status."""
        record = self.get_object()
        field = request.data.get('field')
        value = request.data.get('value')

        allowed_fields = [
            'application_status', 'visa_status', 'enrollment_status',
            'commission_status', 'offer_type', 'offer_date',
            'visa_grant_date', 'enrollment_date',
        ]
        if field not in allowed_fields:
            return Response(
                {'error': f'Cannot update {field}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        setattr(record, field, value)
        record.save(update_fields=[field, 'updated_at'])

        # Auto-update student progression status
        if field == 'enrollment_status' and value == 'Enrolled':
            record.student.progression_status = 'Enrolled Abroad'
            record.student.save(update_fields=['progression_status'])

        return Response(ProgressionRecordSerializer(record).data)

    @action(detail=True, methods=['post'])
    def trigger_commission(self, request, pk=None):
        """Create university commission record and calculate partner commission."""
        record = self.get_object()
        uni = record.university

        if not uni.has_commission_agreement:
            return Response(
                {'error': 'No commission agreement with this university'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get exchange rate
        from apps.core.models import ExchangeRate
        try:
            rate = ExchangeRate.objects.filter(
                from_currency=uni.commission_currency,
                to_currency='BDT'
            ).order_by('-effective_date').first()
            exchange_rate = rate.rate if rate else 1.0
        except ExchangeRate.DoesNotExist:
            exchange_rate = 1.0

        # Calculate commission
        tuition = record.tuition_fee_at_uni or 0
        if uni.commission_type == 'Percentage of Tuition':
            gross = float(tuition) * float(uni.commission_rate) / 100
        elif uni.commission_type == 'Fixed Per Student':
            gross = float(uni.commission_amount or 0)
        else:
            gross = 0

        bdt_amount = gross * float(exchange_rate)

        uni_commission = UniversityCommission.objects.create(
            progression_record=record,
            university=uni,
            student=record.student,
            commission_type=uni.commission_type,
            commission_rate=uni.commission_rate,
            tuition_base=tuition,
            gross_commission=gross,
            commission_currency=uni.commission_currency,
            exchange_rate=exchange_rate,
            commission_in_bdt=bdt_amount,
            status='Expected',
            branch=request.user.branch,
            created_by=request.user,
        )

        # Update progression commission status
        record.commission_status = 'Pending'
        record.save(update_fields=['commission_status', 'updated_at'])

        # Calculate partner commission
        if record.student.partner_id:
            with connection.cursor() as cursor:
                cursor.callproc('sp_calculate_partner_commission', [
                    uni_commission.commission_id,
                    request.user.user_id,
                ])

        return Response(UniversityCommissionSerializer(uni_commission).data)


class UniversityCommissionViewSet(viewsets.ModelViewSet):
    queryset = UniversityCommission.objects.select_related(
        'student', 'university'
    ).all()
    serializer_class = UniversityCommissionSerializer
    filterset_fields = ['status', 'university', 'student', 'branch']
    ordering_fields = ['gross_commission', 'expected_date', 'created_at']

    @action(detail=True, methods=['post'])
    def mark_received(self, request, pk=None):
        """Record that university has paid the commission."""
        commission = self.get_object()
        commission.received_date = request.data.get('received_date')
        commission.received_amount = request.data.get('received_amount')
        commission.received_currency = request.data.get(
            'received_currency', commission.commission_currency
        )
        commission.received_exchange_rate = request.data.get(
            'received_exchange_rate', commission.exchange_rate
        )
        commission.transaction_ref = request.data.get('transaction_ref', '')
        commission.payment_method = request.data.get('payment_method', '')
        commission.received_amount_bdt = (
            float(commission.received_amount) *
            float(commission.received_exchange_rate)
        )
        commission.status = 'Received'
        commission.save()
        return Response(UniversityCommissionSerializer(commission).data)


class PartnerCommissionViewSet(viewsets.ModelViewSet):
    queryset = PartnerCommission.objects.select_related(
        'partner', 'student'
    ).all()
    serializer_class = PartnerCommissionSerializer
    filterset_fields = ['status', 'partner', 'student', 'branch']
    ordering_fields = ['calculated_amount', 'calculated_date']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        commission = self.get_object()
        commission.status = 'Approved'
        commission.approved_by = request.user
        commission.approval_date = request.data.get(
            'approval_date', None
        )
        commission.save()
        return Response(PartnerCommissionSerializer(commission).data)


class PartnerPaymentViewSet(BranchIsolationMixin, viewsets.ModelViewSet):
    queryset = PartnerPayment.objects.select_related('partner').all()
    serializer_class = PartnerPaymentSerializer
    filterset_fields = ['status', 'partner', 'payment_method', 'branch']
    ordering_fields = ['payment_date', 'amount']
