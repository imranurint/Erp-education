from rest_framework import serializers
from .models import (
    ProgressionRecord, UniversityCommission,
    PartnerCommission, PartnerPayment
)


class ProgressionRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_code = serializers.CharField(source='student.student_code', read_only=True)
    university_name = serializers.CharField(source='university.university_name', read_only=True)

    class Meta:
        model = ProgressionRecord
        fields = '__all__'


class UniversityCommissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    university_name = serializers.CharField(source='university.university_name', read_only=True)

    class Meta:
        model = UniversityCommission
        fields = '__all__'


class PartnerCommissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    partner_name = serializers.CharField(source='partner.partner_name', read_only=True)

    class Meta:
        model = PartnerCommission
        fields = '__all__'


class PartnerPaymentSerializer(serializers.ModelSerializer):
    partner_name = serializers.CharField(source='partner.partner_name', read_only=True)

    class Meta:
        model = PartnerPayment
        fields = '__all__'
