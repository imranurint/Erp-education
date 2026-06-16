from celery import shared_task


@shared_task
def process_email_queue():
    """
    Every 5 minutes — send queued emails.
    """
    from apps.notifications.models import EmailQueue
    from django.core.mail import send_mail
    from django.utils import timezone

    pending = EmailQueue.objects.filter(
        status__in=['Queued', 'Retrying']
    ).order_by('-priority', 'created_at')[:50]

    sent = 0
    failed = 0

    for email in pending:
        try:
            send_mail(
                subject=email.subject,
                message=email.body_text or '',
                html_message=email.body_html,
                from_email='noreply@miepathways.com',
                recipient_list=[email.to_email],
                fail_silently=False,
            )
            email.status = 'Sent'
            email.sent_at = timezone.now()
            email.save(update_fields=['status', 'sent_at'])
            sent += 1
        except Exception as e:
            email.attempts += 1
            if email.attempts >= email.max_attempts:
                email.status = 'Failed'
            else:
                email.status = 'Retrying'
            email.error_message = str(e)[:500]
            email.save(update_fields=['status', 'attempts', 'error_message'])
            failed += 1

    return f'Emails: {sent} sent, {failed} failed'


@shared_task
def send_payment_confirmation(payment_id):
    """
    Triggered when payment approved — queue confirmation email.
    """
    from apps.notifications.models import EmailQueue
    from apps.accounting.models import Payment

    try:
        payment = Payment.objects.select_related('student').get(pk=payment_id)
    except Payment.DoesNotExist:
        return 'Payment not found'

    student = payment.student
    if not student.email:
        return 'No email for student'

    EmailQueue.objects.create(
        to_email=student.email,
        to_name=student.full_name,
        subject=f'Payment Confirmation — {payment.receipt_no}',
        body_html=f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #1a365d; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px;">MIE Pathways</h1>
                <p style="margin: 5px 0 0; font-size: 14px;">NCUK International Study Centre</p>
            </div>
            <div style="padding: 25px; background: #f7fafc;">
                <h2 style="color: #2d3748; margin-top: 0;">Payment Confirmation</h2>
                <p>Dear <strong>{student.full_name}</strong>,</p>
                <p>We confirm receipt of your payment:</p>
                <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                    <tr>
                        <td style="padding: 10px; border: 1px solid #e2e8f0; background: #edf2f7;"><strong>Receipt No</strong></td>
                        <td style="padding: 10px; border: 1px solid #e2e8f0;">{payment.receipt_no}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #e2e8f0; background: #edf2f7;"><strong>Date</strong></td>
                        <td style="padding: 10px; border: 1px solid #e2e8f0;">{payment.date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #e2e8f0; background: #edf2f7;"><strong>Amount</strong></td>
                        <td style="padding: 10px; border: 1px solid #e2e8f0;"><strong>BDT {payment.total_amount:,.2f}</strong></td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #e2e8f0; background: #edf2f7;"><strong>Method</strong></td>
                        <td style="padding: 10px; border: 1px solid #e2e8f0;">{payment.payment_method}</td>
                    </tr>
                </table>
                <p>Thank you for your payment.</p>
                <p style="color: #718096; font-size: 12px; margin-top: 30px;">
                    This is an automated email from MIE Pathways. Please do not reply directly.
                </p>
            </div>
        </div>
        ''',
        body_text=(
            f'Dear {student.full_name},\n\n'
            f'Payment confirmed.\n'
            f'Receipt: {payment.receipt_no}\n'
            f'Amount: BDT {payment.total_amount:,.2f}\n'
            f'Date: {payment.date}\n\n'
            f'Thank you.'
        ),
        priority='High',
        reference_type='Payment',
        reference_id=payment_id,
        branch=payment.branch,
    )

    return f'Confirmation queued for {student.email}'


@shared_task
def send_overdue_reminders():
    """
    Weekly Monday 9 AM — send reminders for overdue payments.
    """
    from apps.notifications.models import EmailQueue
    from apps.students.models import StudentDue, Student
    from apps.notifications.models import ScheduledTaskLog
    from django.db.models import Sum
    from django.utils import timezone

    log = ScheduledTaskLog.objects.create(
        task_name='send_overdue_reminders',
        started_at=timezone.now(),
    )

    try:
        # Group overdue by student
        overdue_students = StudentDue.objects.filter(
            status='Overdue'
        ).values('student_id').annotate(
            total_overdue=Sum('due_amount'),
            count=Sum('due_amount') / Sum('due_amount'),  # count trick
        ).filter(total_overdue__gt=0)

        sent_count = 0
        for entry in overdue_students:
            try:
                student = Student.objects.select_related('branch').get(
                    pk=entry['student_id']
                )
            except Student.DoesNotExist:
                continue

            if not student.email:
                continue

            overdue_dues = StudentDue.objects.filter(
                student=student, status='Overdue'
            ).order_by('due_date')

            # Build overdue table rows
            rows = ''
            for d in overdue_dues:
                rows += f'''
                <tr>
                    <td style="padding: 8px; border: 1px solid #e2e8f0;">{d.due_date}</td>
                    <td style="padding: 8px; border: 1px solid #e2e8f0;">{d.coa.coa_name if d.coa else ''}</td>
                    <td style="padding: 8px; border: 1px solid #e2e8f0; text-align: right;">BDT {float(d.due_amount):,.2f}</td>
                </tr>'''

            EmailQueue.objects.create(
                to_email=student.email,
                to_name=student.full_name,
                subject=f'Payment Reminder — MIE Pathways',
                body_html=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #9b2c2c; color: white; padding: 20px; text-align: center;">
                        <h1 style="margin: 0;">MIE Pathways</h1>
                        <p style="margin: 5px 0 0;">Payment Reminder</p>
                    </div>
                    <div style="padding: 25px;">
                        <p>Dear <strong>{student.full_name}</strong>,</p>
                        <p>This is a reminder that you have overdue payments:</p>
                        <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                            <tr style="background: #edf2f7;">
                                <th style="padding: 8px; border: 1px solid #e2e8f0; text-align: left;">Due Date</th>
                                <th style="padding: 8px; border: 1px solid #e2e8f0; text-align: left;">Fee Head</th>
                                <th style="padding: 8px; border: 1px solid #e2e8f0; text-align: right;">Amount</th>
                            </tr>
                            {rows}
                        </table>
                        <p style="font-size: 20px; color: #9b2c2c; font-weight: bold;">
                            Total Overdue: BDT {float(entry["total_overdue"]):,.2f}
                        </p>
                        <p>Please settle your outstanding dues at your earliest convenience.</p>
                        <p>Contact: {student.branch.branch_name if student.branch else "Office"}</p>
                    </div>
                </div>
                ''',
                body_text=(
                    f'Dear {student.full_name},\n\n'
                    f'You have overdue payments totaling BDT {float(entry["total_overdue"]):,.2f}.\n'
                    f'Please settle at your earliest convenience.\n\n'
                    f'MIE Pathways'
                ),
                reference_type='Student',
                reference_id=entry['student_id'],
                branch=student.branch,
            )
            sent_count += 1

        log.status = 'Completed'
        log.finished_at = timezone.now()
        log.records_affected = sent_count
        log.result_summary = f'Sent {sent_count} overdue reminders'
        log.save()

        return f'Overdue reminders sent: {sent_count}'

    except Exception as e:
        log.status = 'Failed'
        log.error_message = str(e)[:500]
        log.finished_at = timezone.now()
        log.save()
        raise