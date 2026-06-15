from django.urls import path
from .views import (
    DashboardView, IncomeStatementView, BalanceSheetView,
    CashFlowView, ProgressionReportView
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view()),
    path('income-statement/', IncomeStatementView.as_view()),
    path('balance-sheet/', BalanceSheetView.as_view()),
    path('cash-flow/', CashFlowView.as_view()),
    path('progression/', ProgressionReportView.as_view()),
]
