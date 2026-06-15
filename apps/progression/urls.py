from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProgressionRecordViewSet, UniversityCommissionViewSet,
    PartnerCommissionViewSet, PartnerPaymentViewSet
)

router = DefaultRouter()
router.register('progression', ProgressionRecordViewSet)
router.register('university-commissions', UniversityCommissionViewSet)
router.register('partner-commissions', PartnerCommissionViewSet)
router.register('partner-payments', PartnerPaymentViewSet)

urlpatterns = [path('', include(router.urls))]
