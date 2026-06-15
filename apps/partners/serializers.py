from rest_framework import serializers
from .models import Partner, University


class PartnerSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Partner
        fields = '__all__'

    def get_student_count(self, obj):
        from apps.students.models import Student
        return Student.objects.filter(partner=obj).count()


class UniversitySerializer(serializers.ModelSerializer):
    placed_students = serializers.SerializerMethodField()

    class Meta:
        model = University
        fields = '__all__'

    def get_placed_students(self, obj):
        from apps.progression.models import ProgressionRecord
        return ProgressionRecord.objects.filter(
            university=obj,
            enrollment_status='Enrolled'
        ).count()
