from rest_framework import serializers
from .models import (
    Student, StudentDocument, StudentFeeSetup, StudentDue, Discount
)


class StudentListSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(source='programme.programme_name', read_only=True)
    programme_code = serializers.CharField(source='programme.code', read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)
    partner_name = serializers.CharField(source='partner.partner_name', read_only=True, default=None)

    class Meta:
        model = Student
        fields = [
            'student_id', 'student_code', 'full_name', 'contact_no', 'email',
            'admission_date', 'programme', 'programme_name', 'programme_code',
            'branch', 'branch_name', 'partner', 'partner_name',
            'referral_source', 'status', 'progression_status',
            'total_fee', 'total_paid', 'total_due',
            'created_at',
        ]


class StudentDetailSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(source='programme.programme_name', read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)
    partner_name = serializers.CharField(source='partner.partner_name', read_only=True, default=None)
    documents = serializers.SerializerMethodField()
    fee_setup = serializers.SerializerMethodField()
    dues = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'

    def get_documents(self, obj):
        docs = StudentDocument.objects.filter(student=obj)
        return StudentDocumentSerializer(docs, many=True).data

    def get_fee_setup(self, obj):
        try:
            setup = StudentFeeSetup.objects.get(student=obj)
            return StudentFeeSetupSerializer(setup).data
        except StudentFeeSetup.DoesNotExist:
            return None

    def get_dues(self, obj):
        dues = StudentDue.objects.filter(student=obj).select_related('coa')
        return StudentDueSerializer(dues, many=True).data


class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ['total_fee', 'total_paid', 'total_due', 'total_discount']

    def create(self, validated_data):
        # Generate student code
        branch_code = validated_data['branch'].branch_code
        year = validated_data['admission_date'].year
        count = Student.objects.filter(
            branch=validated_data['branch'],
            admission_date__year=year
        ).count() + 1
        validated_data['student_code'] = f"STU-{branch_code}-{year}-{count:04d}"
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class StudentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = '__all__'


class StudentFeeSetupSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = StudentFeeSetup
        fields = '__all__'


class StudentDueSerializer(serializers.ModelSerializer):
    coa_name = serializers.CharField(source='coa.coa_name', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = StudentDue
        fields = '__all__'


class DiscountSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = Discount
        fields = '__all__'
