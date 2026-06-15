from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.db import connection
from apps.core.permissions import (
    BranchIsolationMixin, IsAccountantOrAbove, IsCollectorOrAbove
)
from .models import (
    ChartOfAccount, ProgrammeFeeHead, Payment, PaymentItem,
    Voucher, VoucherEntry, MainLedger, StudentLedger,
    PettyCash, LateFeeCharge, FinancialSnapshot
)
from .serializers import (
    ChartOfAccountSerializer, ProgrammeFeeHeadSerializer,
    PaymentSerializer, PaymentCreateSerializer,
    VoucherSerializer, VoucherCreateSerializer,
    MainLedgerSerializer, StudentLedgerSerializer,
    PettyCashSerializer, LateFeeChargeSerializer,
    FinancialSnapshotSerializer, PaymentItemSerializer,
    VoucherEntrySerializer
)


class ChartOfAccountViewSet(viewsets.ModelViewSet):
    queryset = ChartOfAccount.objects.all()
    serializer_class = ChartOfAccountSerializer
    filterset_fields = ['type', 'sub_type', 'is_active', 'is_system', 'is_cash_account']
    search_fields = ['coa_code', 'coa_name']

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Return COA as hierarchical tree."""
        accounts = ChartOfAccount.objects.filter(is_active=True)
        tree = {}
        for acc in accounts:
            parent = acc.parent_code or 'root'
            if parent not in tree:
                tree[parent] = []
            tree[parent].append(ChartOfAccountSerializer(acc).data)
        return Response(tree)

    @action(detail=False, methods=['get'])
    def balances(self, request):
        """Return all account balances from the view."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM v_account_balances")
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(rows)


class ProgrammeFeeHeadViewSet(viewsets.ModelViewSet):
    queryset = ProgrammeFeeHead.objects.select_related('programme', 'coa').all()
    serializer_class = ProgrammeFeeHeadSerializer
    filterset_fields = ['programme', 'is_mandatory', 'is_installable']


class PaymentViewSet(BranchIsolationMixin, viewsets.ModelViewSet):
    queryset = Payment.objects.select_related(
        'student', 'collected_by', 'approved_by', 'bank_coa'
    ).all()
    filterset_fields = [
        'status', 'payment_method', 'student', 'branch', 'date',
    ]
    search_fields = ['receipt_no', 'student__full_name', 'transaction_ref']
    ordering_fields = ['date', 'total_amount', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Calculate total
        items = data['items']
        total = sum(float(item['amount']) for item in items)

        # Generate receipt number
        branch = request.user.branch
        prefix = f"MIE-{branch.branch_code}" if branch else "MIE-XXX"
        year = data['date'].year
        count = Payment.objects.filter(
            branch=branch, date__year=year
        ).count() + 1
        receipt_no = f"{prefix}-{year}-{count:04d}"

        from apps.students.models import Student
        student = Student.objects.get(pk=data['student_id'])

        # Handle exchange rate
        amount_bdt = total
        exchange_rate = 1.0

        payment = Payment.objects.create(
            receipt_no=receipt_no,
            student=student,
            date=data['date'],
            total_amount=total,
            amount_in_bdt=amount_bdt,
            exchange_rate=exchange_rate,
            payment_method=data['payment_method'],
            transaction_ref=data.get('transaction_ref', ''),
            bank_coa_id=data.get('bank_coa_id'),
            collected_by=request.user,
            remarks=data.get('remarks', ''),
            branch=request.user.branch,
        )

        # Create payment items
        for item in items:
            PaymentItem.objects.create(
                payment=payment,
                coa_id=item['coa_id'],
                amount=item['amount'],
                due_id=item.get('due_id'),
                remarks=item.get('remarks', ''),
            )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        payment = self.get_object()
        if payment.status != 'Pending':
            return Response(
                {'error': 'Only pending payments can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Call MySQL stored procedure
        with connection.cursor() as cursor:
            cursor.callproc('sp_approve_payment', [
                payment.payment_id, request.user.user_id
            ])

        payment.refresh_from_db()
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        payment = self.get_object()
        reason = request.data.get('reason', '')
        payment.status = 'Rejected'
        payment.rejection_reason = reason
        payment.approved_by = request.user
        payment.save()
        return Response(PaymentSerializer(payment).data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        pending = self.get_queryset().filter(status='Pending')
        serializer = PaymentSerializer(pending, many=True)
        return Response(serializer.data)


class VoucherViewSet(BranchIsolationMixin, viewsets.ModelViewSet):
    queryset = Voucher.objects.select_related('prepared_by', 'approved_by').all()
    filterset_fields = ['voucher_type', 'status', 'branch', 'date']
    search_fields = ['voucher_no', 'narration']
    ordering_fields = ['date', 'total_debit', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return VoucherCreateSerializer
        return VoucherSerializer

    def create(self, request, *args, **kwargs):
        serializer = VoucherCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        total_debit = sum(float(e.get('debit', 0)) for e in data['entries'])

        branch = request.user.branch
        prefix = "MIE-VOU"
        year = data['date'].year
        count = Voucher.objects.filter(date__year=year).count() + 1
        voucher_no = f"{prefix}-{year}-{count:04d}"

        voucher = Voucher.objects.create(
            voucher_no=voucher_no,
            voucher_type=data['voucher_type'],
            date=data['date'],
            narration=data['narration'],
            total_debit=total_debit,
            total_credit=total_debit,
            prepared_by=request.user,
            branch=request.user.branch,
        )

        for i, entry in enumerate(data['entries'], 1):
            VoucherEntry.objects.create(
                voucher=voucher,
                line_number=i,
                coa_id=entry['coa_id'],
                debit=float(entry.get('debit', 0)),
                credit=float(entry.get('credit', 0)),
                narration=entry.get('narration', ''),
                student_id=entry.get('student_id'),
                partner_id=entry.get('partner_id'),
            )

        return Response(
            VoucherSerializer(voucher).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        voucher = self.get_object()
        if voucher.status not in ('Draft', 'Pending'):
            return Response(
                {'error': 'Voucher cannot be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        with connection.cursor() as cursor:
            cursor.callproc('sp_approve_voucher', [
                voucher.voucher_id, request.user.user_id
            ])
        voucher.refresh_from_db()
        return Response(VoucherSerializer(voucher).data)


class MainLedgerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MainLedger.objects.select_related('coa').all()
    serializer_class = MainLedgerSerializer
    filterset_fields = ['coa', 'branch', 'entry_date', 'reference_type', 'student']
    ordering_fields = ['entry_date', 'debit', 'credit']

    @action(detail=False, methods=['get'])
    def trial_balance(self, request):
        """Generate trial balance."""
        from django.db.models import Sum, F, Q, Case, When, Value, DecimalField
        from django.db.models.functions import Coalesce

        accounts = ChartOfAccount.objects.filter(
            is_active=True
        ).exclude(type='Header')

        result = []
        for acc in accounts:
            agg = MainLedger.objects.filter(coa=acc).aggregate(
                total_debit=Coalesce(Sum('debit'), 0),
                total_credit=Coalesce(Sum('credit'), 0),
            )
            if agg['total_debit'] or agg['total_credit']:
                balance = (
                    agg['total_debit'] - agg['total_credit']
                    if acc.type in ('Asset', 'Expense')
                    else agg['total_credit'] - agg['total_debit']
                )
                result.append({
                    'coa_code': acc.coa_code,
                    'coa_name': acc.coa_name,
                    'type': acc.type,
                    'debit': float(agg['total_debit']),
                    'credit': float(agg['total_credit']),
                    'balance': float(balance),
                })

        return Response(result)


class StudentLedgerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentLedger.objects.select_related('student').all()
    serializer_class = StudentLedgerSerializer
    filterset_fields = ['student', 'branch', 'entry_date']


class PettyCashViewSet(BranchIsolationMixin, viewsets.ModelViewSet):
    queryset = PettyCash.objects.select_related('approved_by').all()
    serializer_class = PettyCashSerializer
    filterset_fields = ['category', 'date', 'branch']
    ordering_fields = ['date', 'amount']


class LateFeeChargeViewSet(viewsets.ModelViewSet):
    queryset = LateFeeCharge.objects.select_related('student').all()
    serializer_class = LateFeeChargeSerializer
    filterset_fields = ['status', 'student', 'branch']

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Run nightly late fee calculation."""
        with connection.cursor() as cursor:
            cursor.callproc('sp_calculate_late_fees')
        return Response({'message': 'Late fees calculated'})


class FinancialSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinancialSnapshot.objects.select_related('branch').all()
    serializer_class = FinancialSnapshotSerializer
    filterset_fields = ['branch', 'snapshot_date']
    ordering_fields = ['snapshot_date']
