from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProgrammeViewSet, AcademicYearViewSet, FiscalPeriodViewSet,
    AcademicRecordViewSet, AttendanceViewSet
)

router = DefaultRouter()
router.register('programmes', ProgrammeViewSet)
router.register('academic-years', AcademicYearViewSet)
router.register('fiscal-periods', FiscalPeriodViewSet)
router.register('academic-records', AcademicRecordViewSet)
router.register('attendance', AttendanceViewSet)

urlpatterns = [path('', include(router.urls))]
