from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection
from django.db.models import Sum, Count, Q
from apps.core.permissions import IsAccountantOrAbove
from apps.students.models import Student
from apps.accounting.models import MainLedger, FinancialSnapshot
from apps.progression.models import ProgressionRecord


class DashboardView(APIView):
    def get(self, request):
        branch_id = request.query_params.get('branch_id')

        # Student metrics
        students = Student.objects.all()
        if branch_id:
            students = students.filter(branch_id=branch_id)

        active = students.filter(status='Active')
        new_month = students.filter(
            admission_date__month=self.request.query_params.get('month'),
            admission_date__year=self.request.query_params.get('year'),
        )

        # Financial metrics from ledger
        ledger = MainLedger.objects.all()
        if branch_id:
            ledger = ledger.filter(branch_id=branch_id)

        from django.utils import timezone
        from datetime import date
        today = date.today()
        month_start = today.replace(day=1)

        month_income = ledger.filter(
            coa__type='Income',
            entry_date__gte=month_start
        ).aggregate(total=Sum('credit'))['total'] or 0

        month_expense = ledger.filter(
            coa__type='Expense',
            entry_date__gte=month_start
        ).aggregate(total=Sum('debit'))['total'] or 0

        return Response({
            'students': {
                'total': students.count(),
                'active': active.count(),
                'new_this_month': new_month.count(),
            },
            'finance': {
                'income_this_month': float(month_income),
                'expense_this_month': float(month_expense),
                'net_this_month': float(month_income - month_expense),
            },
        })


class IncomeStatementView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        branch_id = request.query_params.get('branch_id')

        filters = Q()
        if start_date:
            filters &= Q(entry_date__gte=start_date)
        if end_date:
            filters &= Q(entry_date__lte=end_date)
        if branch_id:
            filters &= Q(branch_id=branch_id)

        income = MainLedger.objects.filter(
            filters, coa__type='Income'
        ).values('coa__coa_code', 'coa__coa_name').annotate(
            amount=Sum('credit') - Sum('debit')
        ).order_by('coa__coa_code')

        expense = MainLedger.objects.filter(
            filters, coa__type='Expense'
        ).values('coa__coa_code', 'coa__coa_name').annotate(
            amount=Sum('debit') - Sum('credit')
        ).order_by('coa__coa_code')

        total_income = sum(float(i['amount']) for i in income)
        total_expense = sum(float(e['amount']) for e in expense)

        return Response({
            'income': list(income),
            'expense': list(expense),
            'total_income': total_income,
            'total_expense': total_expense,
            'net_profit': total_income - total_expense,
        })


class BalanceSheetView(APIView):
    def get(self, request):
        as_date = request.query_params.get('as_date')
        branch_id = request.query_params.get('branch_id')

        filters = Q()
        if as_date:
            filters &= Q(entry_date__lte=as_date)
        if branch_id:
            filters &= Q(branch_id=branch_id)

        def get_balances(account_type):
            return MainLedger.objects.filter(
                filters, coa__type=account_type
            ).values('coa__coa_code', 'coa__coa_name', 'coa__sub_type').annotate(
                total_debit=Sum('debit'),
                total_credit=Sum('credit'),
            ).order_by('coa__coa_code')

        assets = get_balances('Asset')
        liabilities = get_balances('Liability')
        equity = get_balances('Equity')

        def calc_balance(items, account_type):
            result = []
            for item in items:
                d = float(item['total_debit'] or 0)
                c = float(item['total_credit'] or 0)
                if account_type in ('Asset', 'Expense'):
                    balance = d - c
                else:
                    balance = c - d
                result.append({
                    'code': item['coa__coa_code'],
                    'name': item['coa__coa_name'],
                    'sub_type': item['coa__sub_type'],
                    'balance': balance,
                })
            return result

        asset_list = calc_balance(assets, 'Asset')
        liab_list = calc_balance(liabilities, 'Liability')
        equity_list = calc_balance(equity, 'Equity')

        return Response({
            'assets': asset_list,
            'total_assets': sum(a['balance'] for a in asset_list),
            'liabilities': liab_list,
            'total_liabilities': sum(l['balance'] for l in liab_list),
            'equity': equity_list,
            'total_equity': sum(e['balance'] for e in equity_list),
        })


class CashFlowView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        branch_id = request.query_params.get('branch_id')

        filters = Q(coa__is_cash_account=True)
        if start_date:
            filters &= Q(entry_date__gte=start_date)
        if end_date:
            filters &= Q(entry_date__lte=end_date)
        if branch_id:
            filters &= Q(branch_id=branch_id)

        movements = MainLedger.objects.filter(filters).values(
            'coa__coa_code', 'coa__coa_name'
        ).annotate(
            total_inflow=Sum('debit'),
            total_outflow=Sum('credit'),
        )

        return Response({
            'accounts': [
                {
                    'code': m['coa__coa_code'],
                    'name': m['coa__coa_name'],
                    'inflow': float(m['total_inflow'] or 0),
                    'outflow': float(m['total_outflow'] or 0),
                    'net': float(m['total_inflow'] or 0) - float(m['total_outflow'] or 0),
                }
                for m in movements
            ]
        })


class ProgressionReportView(APIView):
    def get(self, request):
        branch_id = request.query_params.get('branch_id')
        records = ProgressionRecord.objects.all()
        if branch_id:
            records = records.filter(branch_id=branch_id)

        total = records.count()
        by_status = records.values('application_status').annotate(count=Count('record_id'))
        by_university = records.values(
            'university__university_name', 'university__country'
        ).annotate(count=Count('record_id'))

        enrolled = records.filter(enrollment_status='Enrolled').count()
        rate = (enrolled / total * 100) if total > 0 else 0

        return Response({
            'total_applications': total,
            'enrolled_abroad': enrolled,
            'progression_rate': round(rate, 1),
            'by_status': list(by_status),
            'by_university': list(by_university),
        })
