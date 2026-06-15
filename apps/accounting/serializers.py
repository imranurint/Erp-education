from rest_framework import serializers
from .models import (
    ChartOfAccount, ProgrammeFeeHead, Payment, PaymentItem,
    Voucher, VoucherEntry, MainLedger, StudentLedger,
    PettyCash, LateFeeCharge, FinancialSnapshot
)


class ChartOfAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartOfAccount
        fields = '__all__'


class ProgrammeFeeHeadSerializer(serializers.ModelSerializer):
    coa_name = serializers.CharField(source='coa.coa_name', read_only=True)
    programme_name = serializers.CharField(source='programme.programme_name', read_only=True)

    class Meta:
        model = ProgrammeFeeHead
        fields = '__all__'


class PaymentItemSerializer(serializers.ModelSerializer):
    coa_name = serializers.CharField(source='coa.coa_name', read_only=True)

    class Meta:
        model = PaymentItem
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_code = serializers.CharField(source='student.student_code', read_only=True)
    collected_by_name = serializers.CharField(source='collected_by.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.name', read_only=True, default=None)
    items = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = '__all__'

    def get_items(self, obj):
        items = PaymentItem.objects.filter(payment=obj).select_related('coa')
        return PaymentItemSerializer(items, many=True).data


class PaymentCreateSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    date = serializers.DateField()
    payment_method = serializers.CharField()
    transaction_ref = serializers.CharField(required=False, allow_blank=True)
    bank_coa_id = serializers.IntegerField(required=False)
    remarks = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(
        child=serializers.DictField()
    )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('At least one payment item required')
        for item in value:
            if 'coa_id' not in item or 'amount' not in item:
                raise serializers.ValidationError('Each item needs coa_id and amount')
        return value


class VoucherEntrySerializer(serializers.ModelSerializer):
    coa_name = serializers.CharField(source='coa.coa_name', read_only=True)
    coa_code = serializers.CharField(source='coa.coa_code', read_only=True)

    class Meta:
        model = VoucherEntry
        fields = '__all__'


class VoucherSerializer(serializers.ModelSerializer):
    prepared_by_name = serializers.CharField(source='prepared_by.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.name', read_only=True, default=None)
    entries = serializers.SerializerMethodField()

    class Meta:
        model = Voucher
        fields = '__all__'

    def get_entries(self, obj):
        entries = VoucherEntry.objects.filter(voucher=obj).select_related('coa')
        return VoucherEntrySerializer(entries, many=True).data


class VoucherCreateSerializer(serializers.Serializer):
    voucher_type = serializers.CharField()
    date = serializers.DateField()
    narration = serializers.CharField()
    entries = serializers.ListField(child=serializers.DictField())

    def validate_entries(self, value):
        if len(value) < 2:
            raise serializers.ValidationError('Minimum 2 entries required (debit + credit)')
        total_debit = sum(float(e.get('debit', 0)) for e in value)
        total_credit = sum(float(e.get('credit', 0)) for e in value)
        if abs(total_debit - total_credit) > 0.01:
            raise serializers.ValidationError(
                f'Debit ({total_debit}) must equal Credit ({total_credit})'
            )
        return value


class MainLedgerSerializer(serializers.ModelSerializer):
    coa_name = serializers.CharField(source='coa.coa_name', read_only=True)
    coa_code = serializers.CharField(source='coa.coa_code', read_only=True)

    class Meta:
        model = MainLedger
        fields = '__all__'


class StudentLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentLedger
        fields = '__all__'


class PettyCashSerializer(serializers.ModelSerializer):
    class Meta:
        model = PettyCash
        fields = '__all__'


class LateFeeChargeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = LateFeeCharge
        fields = '__all__'


class FinancialSnapshotSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)

    class Meta:
        model = FinancialSnapshot
        fields = '__all__'
