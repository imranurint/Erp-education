from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChartOfAccountViewSet, ProgrammeFeeHeadViewSet, PaymentViewSet,
    VoucherViewSet, MainLedgerViewSet, StudentLedgerViewSet,
    PettyCashViewSet, LateFeeChargeViewSet, FinancialSnapshotViewSet
)

router = DefaultRouter()
router.register('coa', ChartOfAccountViewSet)
router.register('fee-heads', ProgrammeFeeHeadViewSet)
router.register('payments', PaymentViewSet)
router.register('vouchers', VoucherViewSet)
router.register('main-ledger', MainLedgerViewSet)
router.register('student-ledger', StudentLedgerViewSet)
router.register('petty-cash', PettyCashViewSet)
router.register('late-fees', LateFeeChargeViewSet)
router.register('snapshots', FinancialSnapshotViewSet)

urlpatterns = [path('', include(router.urls))]
