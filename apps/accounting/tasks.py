from celery import shared_task
from datetime import date
from django.db.models import Sum


@shared_task
def calculate_late_fees():
    """
    Nightly 1 AM — find overdue unpaid dues, calculate 2% late fee.
    """
    from apps.accounting.models import StudentDue
    from apps.notifications.models import ScheduledTaskLog
    from django.utils import timezone

    log = ScheduledTaskLog.objects.create(
        task_name='calculate_late_fees',
        started_at=timezone.now(),
    )

    try:
        overdue_dues = StudentDue.objects.filter(
            status__in=['Unpaid', 'Overdue'],
            due_date__lt=date.today(),
        )

        updated = 0
        for due in overdue_dues:
            due.status = 'Overdue'
            due.save(update_fields=['status'])
            updated += 1

            # Calculate late fee (2% per month)
            days = (date.today() - due.due_date).days
            if days > 30:
                months = days // 30
                late_fee_rate = 0.02
                late_fee = float(due.due_amount) * late_fee_rate * months
                max_fee = float(due.amount) * 0.10  # 10% cap
                late_fee = min(late_fee, max_fee)

                # Create late fee charge
                from apps.accounting.models import LateFeeCharge
                existing = LateFeeCharge.objects.filter(
                    student=due.student, due=due,
                    status='Calculated'
                ).exists()

                if not existing and late_fee > 0:
                    LateFeeCharge.objects.create(
                        student=due.student,
                        due=due,
                        charge_date=date.today(),
                        original_amount=due.due_amount,
                        days_overdue=days,
                        late_fee_percent=2.00,
                        late_fee_amount=round(late_fee),
                        status='Calculated',
                        branch=due.branch,
                    )

        log.status = 'Completed'
        log.finished_at = timezone.now()
        log.records_affected = updated
        log.result_summary = f'Updated {updated} overdue dues'
        log.save()

        return f'Late fees processed: {updated} dues updated'

    except Exception as e:
        log.status = 'Failed'
        log.error_message = str(e)[:500]
        log.finished_at = timezone.now()
        log.save()
        raise


@shared_task
def generate_monthly_snapshot():
    """
    1st of month 2 AM — generate financial snapshot for previous month.
    """
    from datetime import date, timedelta
    from apps.accounting.models import MainLedger, FinancialSnapshot, Payment
    from apps.students.models import Student
    from apps.core.models import Branch
    from apps.notifications.models import ScheduledTaskLog
    from django.utils import timezone

    log = ScheduledTaskLog.objects.create(
        task_name='generate_monthly_snapshot',
        started_at=timezone.now(),
    )

    try:
        today = date.today()
        last_month_end = today.replace(day=1) - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        for branch in Branch.objects.filter(status='Active'):
            ledger = MainLedger.objects.filter(branch=branch)

            income = ledger.filter(
                coa__type='Income',
                entry_date__range=[last_month_start, last_month_end]
            ).aggregate(t=Sum('credit'))['t'] or 0

            expense = ledger.filter(
                coa__type='Expense',
                entry_date__range=[last_month_start, last_month_end]
            ).aggregate(t=Sum('debit'))['t'] or 0

            students = Student.objects.filter(branch=branch)
            payments = Payment.objects.filter(
                branch=branch, status='Approved',
                date__range=[last_month_start, last_month_end]
            )

            FinancialSnapshot.objects.update_or_create(
                snapshot_date=last_month_end,
                branch=branch,
                defaults={
                    'total_income': income,
                    'total_expense': expense,
                    'net_profit': float(income) - float(expense),
                    'total_students': students.count(),
                    'active_students': students.filter(status='Active').count(),
                    'new_admissions': students.filter(
                        admission_date__range=[last_month_start, last_month_end]
                    ).count(),
                    'total_collections': payments.aggregate(t=Sum('amount_in_bdt'))['t'] or 0,
                }
            )

        log.status = 'Completed'
        log.finished_at = timezone.now()
        log.result_summary = f'Snapshot for {last_month_end.strftime("%B %Y")}'
        log.save()

        return f'Snapshot generated for {last_month_end.strftime("%B %Y")}'

    except Exception as e:
        log.status = 'Failed'
        log.error_message = str(e)[:500]
        log.finished_at = timezone.now()
        log.save()
        raise