import os
from datetime import datetime
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)


# ── Company Info ───────────────────────────────────────────
COMPANY = 'MIE Pathways'
TAGLINE = 'NCUK International Study Centre'
ADDR_DHK = 'Gulshan-2, Dhaka 1212, Bangladesh'
ADDR_CTG = 'Agrabad C/A, Chattogram 4100, Bangladesh'
PHONE = '+880-2-9876543'
EMAIL = 'info@miepathways.com'


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle('Company', fontSize=16, fontName='Helvetica-Bold',
                         alignment=TA_CENTER, spaceAfter=2,
                         textColor=colors.HexColor('#1a365d')))
    s.add(ParagraphStyle('Tagline', fontSize=9, fontName='Helvetica',
                         alignment=TA_CENTER, spaceAfter=1,
                         textColor=colors.HexColor('#4a5568')))
    s.add(ParagraphStyle('Title', fontSize=13, fontName='Helvetica-Bold',
                         alignment=TA_CENTER, spaceBefore=10, spaceAfter=6,
                         textColor=colors.HexColor('#2d3748')))
    s.add(ParagraphStyle('Section', fontSize=10, fontName='Helvetica-Bold',
                         spaceBefore=8, spaceAfter=3,
                         textColor=colors.HexColor('#2d3748')))
    s.add(ParagraphStyle('Small', fontSize=7, fontName='Helvetica',
                         alignment=TA_RIGHT, textColor=colors.HexColor('#718096')))
    s.add(ParagraphStyle('SmallL', fontSize=7, fontName='Helvetica',
                         alignment=TA_LEFT, textColor=colors.HexColor('#718096')))
    s.add(ParagraphStyle('Right', fontSize=9, fontName='Helvetica',
                         alignment=TA_RIGHT))
    return s


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(colors.HexColor('#718096'))
    canvas.drawString(25 * mm, 10 * mm, f'{COMPANY} — Confidential')
    canvas.drawRightString(A4[0] - 25 * mm, 10 * mm, f'Page {doc.page}')
    canvas.drawRightString(A4[0] - 25 * mm, 15 * mm,
                           f'Generated: {datetime.now().strftime("%d %b %Y %H:%M")}')
    canvas.setStrokeColor(colors.HexColor('#e2e8f0'))
    canvas.line(25 * mm, 18 * mm, A4[0] - 25 * mm, 18 * mm)
    canvas.restoreState()


def _header(elements, s, branch_name=None):
    elements.append(Paragraph(COMPANY, s['Company']))
    elements.append(Paragraph(TAGLINE, s['Tagline']))
    if branch_name:
        addr = ADDR_CTG if 'Chattogram' in str(branch_name) else ADDR_DHK
        elements.append(Paragraph(f'{branch_name} — {addr}', s['Tagline']))
    elements.append(Spacer(1, 3 * mm))


def _doc(filepath):
    return SimpleDocTemplate(filepath, pagesize=A4,
                             leftMargin=25 * mm, rightMargin=25 * mm,
                             topMargin=20 * mm, bottomMargin=25 * mm)


def _table_style(header_bg='#1a365d'):
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -2), 0.4, colors.HexColor('#e2e8f0')),
        ('LINEABOVE', (0, -1), (-1, -1), 1.2, colors.HexColor(header_bg)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f7fafc')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ])


def _save_dir(sub='receipts'):
    d = os.path.join(settings.MEDIA_ROOT, sub)
    os.makedirs(d, exist_ok=True)
    return d


# ══════════════════════════════════════════════════════════
# RECEIPT
# ══════════════════════════════════════════════════════════
def generate_receipt_pdf(payment):
    """Generate receipt PDF. Returns (filepath, filename)."""
    from apps.accounting.models import PaymentItem

    s = _styles()
    save_dir = _save_dir('receipts')
    filename = f'receipt_{payment.receipt_no}.pdf'
    filepath = os.path.join(save_dir, filename)
    doc = _doc(filepath)
    els = []

    student = payment.student
    branch = payment.branch.branch_name if payment.branch else None
    _header(els, s, branch)
    els.append(Paragraph('PAYMENT RECEIPT', s['Title']))
    els.append(Spacer(1, 3 * mm))

    # Info
    info = [
        ['Receipt No:', str(payment.receipt_no), 'Date:', str(payment.date)],
        ['Student:', student.full_name, 'ID:', student.student_code],
        ['Programme:', student.programme.programme_name if student.programme else '',
         'Contact:', student.contact_no or ''],
        ['Method:', payment.payment_method,
         'Ref:', payment.transaction_ref or 'N/A'],
    ]
    t = Table(info, colWidths=[28 * mm, 55 * mm, 25 * mm, 52 * mm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#4a5568')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    els.append(t)
    els.append(Spacer(1, 5 * mm))

    # Items
    els.append(Paragraph('Payment Details', s['Section']))
    items = PaymentItem.objects.filter(payment=payment).select_related('coa')
    data = [['#', 'Fee Head', 'Amount (BDT)']]
    for i, item in enumerate(items, 1):
        data.append([str(i), item.coa.coa_name, f'{float(item.amount):,.2f}'])
    data.append(['', 'TOTAL', f'{float(payment.total_amount):,.2f}'])

    it = Table(data, colWidths=[10 * mm, 100 * mm, 40 * mm])
    it.setStyle(_table_style())
    els.append(it)

    els.append(Spacer(1, 12 * mm))
    els.append(Paragraph(f'Collected by: _________________________', s['Small']))
    els.append(Spacer(1, 2 * mm))
    els.append(Paragraph(f'System-generated receipt. Ref: {payment.receipt_no}', s['Small']))

    doc.build(els, onFirstPage=_footer, onLaterPages=_footer)
    return filepath, filename


# ══════════════════════════════════════════════════════════
# PAYSLIP
# ══════════════════════════════════════════════════════════
def generate_payslip_pdf(payroll_item, payroll):
    """Generate payslip PDF. Returns (filepath, filename)."""
    s = _styles()
    save_dir = _save_dir('payslips')
    emp = payroll_item.employee
    fname = f'payslip_{emp.employee_code}_{payroll.period_label.replace(" ", "_")}.pdf'
    filepath = os.path.join(save_dir, fname)
    doc = _doc(filepath)
    els = []

    _header(els, s)
    els.append(Paragraph(f'PAYSLIP — {payroll.period_label}', s['Title']))
    els.append(Spacer(1, 3 * mm))

    info = [
        ['Employee:', emp.user.name, 'Code:', emp.employee_code],
        ['Department:', emp.department.department_name if emp.department else '',
         'Designation:', emp.designation.designation_name if emp.designation else ''],
        ['Days Worked:', str(payroll_item.days_worked),
         'Absent:', str(payroll_item.days_absent)],
        ['Overtime:', f'{float(payroll_item.overtime_hours):.1f} hrs', '', ''],
    ]
    t = Table(info, colWidths=[28 * mm, 55 * mm, 25 * mm, 52 * mm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    els.append(t)
    els.append(Spacer(1, 5 * mm))

    # Earnings
    earnings = [
        ['EARNINGS', 'Amount (BDT)'],
        ['Basic Salary', f'{float(payroll_item.basic_salary):,.2f}'],
        ['House Rent', f'{float(payroll_item.house_rent):,.2f}'],
        ['Medical Allowance', f'{float(payroll_item.medical_allowance):,.2f}'],
        ['Transport Allowance', f'{float(payroll_item.transport_allowance):,.2f}'],
        ['Food Allowance', f'{float(payroll_item.food_allowance):,.2f}'],
        ['Overtime Pay', f'{float(payroll_item.overtime_amount):,.2f}'],
        ['Bonus', f'{float(payroll_item.bonus):,.2f}'],
        ['GROSS TOTAL', f'{float(payroll_item.gross_salary):,.2f}'],
    ]
    # Deductions
    deductions = [
        ['DEDUCTIONS', 'Amount (BDT)'],
        ['Provident Fund', f'{float(payroll_item.provident_fund):,.2f}'],
        ['Tax', f'{float(payroll_item.tax_deduction):,.2f}'],
        ['Insurance', f'{float(payroll_item.insurance_deduction):,.2f}'],
        ['Absent Deduction', f'{float(payroll_item.absent_deduction):,.2f}'],
        ['Advance', f'{float(payroll_item.advance_deduction):,.2f}'],
        ['Loan', f'{float(payroll_item.loan_deduction):,.2f}'],
        ['', ''],
        ['TOTAL DEDUCTIONS', f'{float(payroll_item.total_deduction):,.2f}'],
    ]

    earn_t = Table(earnings, colWidths=[50 * mm, 30 * mm])
    earn_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#276749')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0fff4')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -2), 0.4, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))

    ded_t = Table(deductions, colWidths=[50 * mm, 30 * mm])
    ded_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b2c2c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fff5f5')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -2), 0.4, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))

    combined = Table([[earn_t, '', ded_t]], colWidths=[82 * mm, 6 * mm, 82 * mm])
    els.append(combined)
    els.append(Spacer(1, 6 * mm))

    # Net
    net_data = [['NET SALARY', f'BDT {float(payroll_item.net_salary):,.2f}']]
    net_t = Table(net_data, colWidths=[80 * mm, 80 * mm])
    net_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    els.append(net_t)

    els.append(Spacer(1, 10 * mm))
    els.append(Paragraph(
        f'Bank: {emp.bank_name or "N/A"} | Account: {emp.bank_account_no or "N/A"}',
        s['Small']
    ))

    doc.build(els, onFirstPage=_footer, onLaterPages=_footer)
    return filepath, fname


# ══════════════════════════════════════════════════════════
# INCOME STATEMENT
# ══════════════════════════════════════════════════════════
def generate_income_statement_pdf(start_date, end_date, branch_id=None):
    """Generate Income Statement PDF. Returns (filepath, filename)."""
    from django.db.models import Sum, Q
    from apps.accounting.models import MainLedger

    s = _styles()
    save_dir = _save_dir('reports')
    period = f'{start_date} to {end_date}'
    fname = f'income_statement_{start_date}_{end_date}.pdf'
    filepath = os.path.join(save_dir, fname)
    doc = _doc(filepath)
    els = []

    branch_name = None
    if branch_id:
        from apps.core.models import Branch
        branch_name = Branch.objects.get(pk=branch_id).branch_name

    _header(els, s, branch_name)
    els.append(Paragraph('INCOME STATEMENT', s['Title']))
    els.append(Paragraph(f'Period: {period}', s['Tagline']))
    els.append(Spacer(1, 5 * mm))

    filters = Q(entry_date__gte=start_date, entry_date__lte=end_date)
    if branch_id:
        filters &= Q(branch_id=branch_id)

    # Income
    income = MainLedger.objects.filter(
        filters, coa__type='Income'
    ).values('coa__coa_code', 'coa__coa_name').annotate(
        amount=Sum('credit') - Sum('debit')
    ).order_by('coa__coa_code')

    els.append(Paragraph('Income', s['Section']))
    inc_data = [['Code', 'Account', 'Amount (BDT)']]
    total_income = 0
    for item in income:
        amt = float(item['amount'] or 0)
        total_income += amt
        inc_data.append([item['coa__coa_code'], item['coa__coa_name'], f'{amt:,.2f}'])
    inc_data.append(['', 'TOTAL INCOME', f'{total_income:,.2f}'])

    inc_t = Table(inc_data, colWidths=[18 * mm, 92 * mm, 40 * mm])
    inc_t.setStyle(_table_style('#276749'))
    els.append(inc_t)
    els.append(Spacer(1, 5 * mm))

    # Expenses
    expense = MainLedger.objects.filter(
        filters, coa__type='Expense'
    ).values('coa__coa_code', 'coa__coa_name').annotate(
        amount=Sum('debit') - Sum('credit')
    ).order_by('coa__coa_code')

    els.append(Paragraph('Expenses', s['Section']))
    exp_data = [['Code', 'Account', 'Amount (BDT)']]
    total_expense = 0
    for item in expense:
        amt = float(item['amount'] or 0)
        total_expense += amt
        exp_data.append([item['coa__coa_code'], item['coa__coa_name'], f'{amt:,.2f}'])
    exp_data.append(['', 'TOTAL EXPENSES', f'{total_expense:,.2f}'])

    exp_t = Table(exp_data, colWidths=[18 * mm, 92 * mm, 40 * mm])
    exp_t.setStyle(_table_style('#9b2c2c'))
    els.append(exp_t)
    els.append(Spacer(1, 6 * mm))

    # Net Profit
    profit = total_income - total_expense
    pc = '#276749' if profit >= 0 else '#9b2c2c'
    pf = 'NET PROFIT' if profit >= 0 else 'NET LOSS'
    pn = Table([[pf, f'BDT {profit:,.2f}']], colWidths=[80 * mm, 80 * mm])
    pn.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(pc)),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    els.append(pn)

    doc.build(els, onFirstPage=_footer, onLaterPages=_footer)
    return filepath, fname


# ══════════════════════════════════════════════════════════
# BALANCE SHEET
# ══════════════════════════════════════════════════════════
def generate_balance_sheet_pdf(as_of_date, branch_id=None):
    """Generate Balance Sheet PDF. Returns (filepath, filename)."""
    from django.db.models import Sum, Q
    from apps.accounting.models import MainLedger

    s = _styles()
    save_dir = _save_dir('reports')
    fname = f'balance_sheet_{as_of_date}.pdf'
    filepath = os.path.join(save_dir, fname)
    doc = _doc(filepath)
    els = []

    branch_name = None
    if branch_id:
        from apps.core.models import Branch
        branch_name = Branch.objects.get(pk=branch_id).branch_name

    _header(els, s, branch_name)
    els.append(Paragraph('BALANCE SHEET', s['Title']))
    els.append(Paragraph(f'As at: {as_of_date}', s['Tagline']))
    els.append(Spacer(1, 5 * mm))

    filters = Q(entry_date__lte=as_of_date)
    if branch_id:
        filters &= Q(branch_id=branch_id)

    # Assets
    assets = MainLedger.objects.filter(
        filters, coa__type='Asset'
    ).values('coa__coa_code', 'coa__coa_name').annotate(
        balance=Sum('debit') - Sum('credit')
    ).order_by('coa__coa_code')

    els.append(Paragraph('ASSETS', s['Section']))
    ast_data = [['Code', 'Account', 'Balance (BDT)']]
    total_assets = 0
    for item in assets:
        bal = float(item['balance'] or 0)
        if bal != 0:
            total_assets += bal
            ast_data.append([item['coa__coa_code'], item['coa__coa_name'], f'{bal:,.2f}'])
    ast_data.append(['', 'TOTAL ASSETS', f'{total_assets:,.2f}'])

    ast_t = Table(ast_data, colWidths=[18 * mm, 92 * mm, 40 * mm])
    ast_t.setStyle(_table_style('#2b6cb0'))
    els.append(ast_t)
    els.append(Spacer(1, 5 * mm))

    # Liabilities
    liabs = MainLedger.objects.filter(
        filters, coa__type='Liability'
    ).values('coa__coa_code', 'coa__coa_name').annotate(
        balance=Sum('credit') - Sum('debit')
    ).order_by('coa__coa_code')

    els.append(Paragraph('LIABILITIES', s['Section']))
    liab_data = [['Code', 'Account', 'Balance (BDT)']]
    total_liab = 0
    for item in liabs:
        bal = float(item['balance'] or 0)
        if bal != 0:
            total_liab += bal
            liab_data.append([item['coa__coa_code'], item['coa__coa_name'], f'{bal:,.2f}'])
    liab_data.append(['', 'TOTAL LIABILITIES', f'{total_liab:,.2f}'])

    liab_t = Table(liab_data, colWidths=[18 * mm, 92 * mm, 40 * mm])
    liab_t.setStyle(_table_style('#9b2c2c'))
    els.append(liab_t)
    els.append(Spacer(1, 5 * mm))

    # Equity
    equity = MainLedger.objects.filter(
        filters, coa__type='Equity'
    ).values('coa__coa_code', 'coa__coa_name').annotate(
        balance=Sum('credit') - Sum('debit')
    ).order_by('coa__coa_code')

    els.append(Paragraph('EQUITY', s['Section']))
    eq_data = [['Code', 'Account', 'Balance (BDT)']]
    total_eq = 0
    for item in equity:
        bal = float(item['balance'] or 0)
        if bal != 0:
            total_eq += bal
            eq_data.append([item['coa__coa_code'], item['coa__coa_name'], f'{bal:,.2f}'])
    eq_data.append(['', 'TOTAL EQUITY', f'{total_eq:,.2f}'])

    eq_t = Table(eq_data, colWidths=[18 * mm, 92 * mm, 40 * mm])
    eq_t.setStyle(_table_style('#276749'))
    els.append(eq_t)
    els.append(Spacer(1, 6 * mm))

    # Check
    diff = total_assets - (total_liab + total_eq)
    check_label = 'BALANCED' if abs(diff) < 1 else f'DIFFERENCE: {diff:,.2f}'
    check_color = '#276749' if abs(diff) < 1 else '#9b2c2c'
    ck = Table([[f'Assets = Liabilities + Equity', check_label]],
               colWidths=[90 * mm, 70 * mm])
    ck.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(check_color)),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    els.append(ck)

    doc.build(els, onFirstPage=_footer, onLaterPages=_footer)
    return filepath, fname


# ══════════════════════════════════════════════════════════
# STUDENT STATEMENT
# ══════════════════════════════════════════════════════════
def generate_student_statement_pdf(student):
    """Generate student fee statement. Returns (filepath, filename)."""
    from apps.accounting.models import StudentLedger, StudentDue
    from apps.accounting.models import Payment

    s = _styles()
    save_dir = _save_dir('statements')
    fname = f'statement_{student.student_code}.pdf'
    filepath = os.path.join(save_dir, fname)
    doc = _doc(filepath)
    els = []

    branch = student.branch.branch_name if student.branch else None
    _header(els, s, branch)
    els.append(Paragraph('STUDENT FEE STATEMENT', s['Title']))
    els.append(Spacer(1, 3 * mm))

    info = [
        ['Student:', student.full_name, 'Code:', student.student_code],
        ['Programme:', student.programme.programme_name if student.programme else '',
         'Status:', student.status],
        ['Admission:', str(student.admission_date), 'Contact:', student.contact_no or ''],
    ]
    t = Table(info, colWidths=[28 * mm, 55 * mm, 25 * mm, 52 * mm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    els.append(t)
    els.append(Spacer(1, 5 * mm))

    # Fee Summary
    els.append(Paragraph('Fee Summary', s['Section']))
    fee_data = [
        ['', 'Amount (BDT)'],
        ['Total Fee', f'{float(student.total_fee):,.2f}'],
        ['Total Paid', f'{float(student.total_paid):,.2f}'],
        ['Total Due', f'{float(student.total_due):,.2f}'],
    ]
    ft = Table(fee_data, colWidths=[80 * mm, 40 * mm])
    ft.setStyle(_table_style())
    els.append(ft)
    els.append(Spacer(1, 5 * mm))

    # Dues Detail
    els.append(Paragraph('Installment Details', s['Section']))
    dues = StudentDue.objects.filter(student=student).order_by('due_date', 'installment_no')
    dd = [['#', 'Fee Head', 'Due Date', 'Amount', 'Paid', 'Balance', 'Status']]
    for i, d in enumerate(dues, 1):
        dd.append([
            str(i), d.coa.coa_name if d.coa else '',
            str(d.due_date), f'{float(d.amount):,.2f}',
            f'{float(d.paid_amount):,.2f}', f'{float(d.due_amount):,.2f}',
            d.status
        ])

    dt = Table(dd, colWidths=[8 * mm, 40 * mm, 22 * mm, 22 * mm, 22 * mm, 22 * mm, 18 * mm])
    dt.setStyle(_table_style())
    els.append(dt)
    els.append(Spacer(1, 5 * mm))

    # Payment History
    els.append(Paragraph('Payment History', s['Section']))
    payments = Payment.objects.filter(
        student=student, status='Approved'
    ).order_by('date')
    pd = [['#', 'Receipt', 'Date', 'Method', 'Amount (BDT)']]
    for i, p in enumerate(payments, 1):
        pd.append([str(i), p.receipt_no, str(p.date), p.payment_method,
                    f'{float(p.total_amount):,.2f}'])

    pt = Table(pd, colWidths=[8 * mm, 45 * mm, 25 * mm, 30 * mm, 30 * mm])
    pt.setStyle(_table_style())
    els.append(pt)

    doc.build(els, onFirstPage=_footer, onLaterPages=_footer)
    return filepath, fname


# ══════════════════════════════════════════════════════════
# INVOICE (for unpaid dues)
# ══════════════════════════════════════════════════════════
def generate_invoice_pdf(student):
    """Generate invoice for unpaid dues. Returns (filepath, filename)."""
    from apps.accounting.models import StudentDue

    s = _styles()
    save_dir = _save_dir('invoices')
    fname = f'invoice_{student.student_code}.pdf'
    filepath = os.path.join(save_dir, fname)
    doc = _doc(filepath)
    els = []

    branch = student.branch.branch_name if student.branch else None
    _header(els, s, branch)
    els.append(Paragraph('FEE INVOICE', s['Title']))
    els.append(Spacer(1, 3 * mm))

    info = [
        ['Student:', student.full_name, 'Code:', student.student_code],
        ['Programme:', student.programme.programme_name if student.programme else '',
         'Contact:', student.contact_no or ''],
        ['Invoice Date:', datetime.now().strftime('%Y-%m-%d'), '', ''],
    ]
    t = Table(info, colWidths=[28 * mm, 55 * mm, 25 * mm, 52 * mm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    els.append(t)
    els.append(Spacer(1, 5 * mm))

    unpaid = StudentDue.objects.filter(
        student=student, status__in=['Unpaid', 'Overdue', 'Partial']
    ).order_by('due_date')

    els.append(Paragraph('Outstanding Dues', s['Section']))
    data = [['#', 'Fee Head', 'Due Date', 'Amount (BDT)', 'Paid', 'Outstanding', 'Status']]
    total_due = 0
    for i, d in enumerate(unpaid, 1):
        total_due += float(d.due_amount)
        data.append([
            str(i), d.coa.coa_name if d.coa else '',
            str(d.due_date), f'{float(d.amount):,.2f}',
            f'{float(d.paid_amount):,.2f}', f'{float(d.due_amount):,.2f}',
            d.status
        ])
    data.append(['', '', '', '', 'TOTAL DUE', f'{total_due:,.2f}', ''])

    dt = Table(data, colWidths=[8 * mm, 35 * mm, 22 * mm, 22 * mm, 22 * mm, 25 * mm, 18 * mm])
    dt.setStyle(_table_style('#9b2c2c'))
    els.append(dt)

    els.append(Spacer(1, 8 * mm))
    els.append(Paragraph(
        'Please settle the above amount at your earliest convenience.', s['SmallL']))
    els.append(Paragraph(
        f'Late fee of 2% per month will be applied after due date.', s['SmallL']))

    doc.build(els, onFirstPage=_footer, onLaterPages=_footer)
    return filepath, fname