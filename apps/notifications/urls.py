from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmailQueueViewSet, GeneratedDocumentViewSet,
    ScheduledTaskLogViewSet,
    download_receipt, download_payslip,
    download_income_statement, download_balance_sheet,
    download_student_statement, download_invoice,
)

router = DefaultRouter()
router.register('email-queue', EmailQueueViewSet)
router.register('generated-documents', GeneratedDocumentViewSet)
router.register('task-logs', ScheduledTaskLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # PDF Downloads
    path('documents/receipt/<int:payment_id>/',
         download_receipt, name='download-receipt'),
    path('documents/payslip/<int:payroll_item_id>/',
         download_payslip, name='download-payslip'),
    path('documents/income-statement/',
         download_income_statement, name='download-income-statement'),
    path('documents/balance-sheet/',
         download_balance_sheet, name='download-balance-sheet'),
    path('documents/student-statement/<int:student_id>/',
         download_student_statement, name='download-student-statement'),
    path('documents/invoice/<int:student_id>/',
         download_invoice, name='download-invoice'),
]