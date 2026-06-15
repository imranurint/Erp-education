from rest_framework import serializers
from .models import Programme, AcademicYear, FiscalPeriod, AcademicRecord, Attendance


class ProgrammeSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Programme
        fields = '__all__'

    def get_student_count(self, obj):
        from apps.students.models import Student
        return Student.objects.filter(
            programme=obj, status='Active'
        ).count()


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'


class FiscalPeriodSerializer(serializers.ModelSerializer):
    year_name = serializers.CharField(source='year.year_name', read_only=True)

    class Meta:
        model = FiscalPeriod
        fields = '__all__'


class AcademicRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_code = serializers.CharField(source='student.student_code', read_only=True)
    programme_name = serializers.CharField(source='programme.programme_name', read_only=True)

    class Meta:
        model = AcademicRecord
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'


class BulkAttendanceSerializer(serializers.Serializer):
    attendance_date = serializers.DateField()
    programme_id = serializers.IntegerField()
    session_type = serializers.CharField(default='Lecture')
    records = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
