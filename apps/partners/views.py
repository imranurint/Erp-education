from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Partner, University
from .serializers import PartnerSerializer, UniversitySerializer


class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    filterset_fields = ['status', 'partner_type', 'country', 'branch']
    search_fields = ['partner_name', 'partner_code', 'contact_person', 'city']

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        partner = self.get_object()
        from apps.students.models import Student
        from apps.students.serializers import StudentListSerializer
        students = Student.objects.filter(partner=partner)
        return Response(StudentListSerializer(students, many=True).data)

    @action(detail=True, methods=['get'])
    def commissions(self, request, pk=None):
        partner = self.get_object()
        from apps.progression.models import PartnerCommission
        from apps.progression.serializers import PartnerCommissionSerializer
        commissions = PartnerCommission.objects.filter(partner=partner)
        return Response(PartnerCommissionSerializer(commissions, many=True).data)


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    filterset_fields = ['country', 'status', 'has_commission_agreement']
    search_fields = ['university_name', 'city', 'country']

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        university = self.get_object()
        from apps.progression.models import ProgressionRecord
        from apps.progression.serializers import ProgressionRecordSerializer
        records = ProgressionRecord.objects.filter(university=university)
        return Response(ProgressionRecordSerializer(records, many=True).data)
