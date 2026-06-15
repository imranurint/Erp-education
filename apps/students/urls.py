from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet, StudentDocumentViewSet,
    StudentFeeSetupViewSet, StudentDueViewSet, DiscountViewSet
)

router = DefaultRouter()
router.register('students', StudentViewSet)
router.register('documents', StudentDocumentViewSet)
router.register('fee-setups', StudentFeeSetupViewSet)
router.register('dues', StudentDueViewSet)
router.register('discounts', DiscountViewSet)

urlpatterns = [path('', include(router.urls))]
