import random
import calendar
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.core.models import Branch, User, ExchangeRate
from apps.academics.models import (
    Programme, AcademicYear, FiscalPeriod, AcademicRecord, Attendance
)
from apps.students.models import (
    Student, StudentDocument, StudentFeeSetup, StudentDue, Discount
)
from apps.partners.models import Partner, University
from apps.accounting.models import (
    ChartOfAccount, ProgrammeFeeHead, Payment, PaymentItem,
    Voucher, VoucherEntry, MainLedger, StudentLedger, PettyCash
)
from apps.progression.models import (
    ProgressionRecord, UniversityCommission, PartnerCommission, PartnerPayment
)
from django.db import models


class Command(BaseCommand):
    help = 'Seed all tables with realistic demo data using Django ORM'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('  MIE PATHWAYS — ORM SEED'))
        self.stdout.write(self.style.WARNING('=' * 60))

        # ─────────────────────────────────────────────────────
        # 1. CHART OF ACCOUNTS
        # ─────────────────────────────────────────────────────
        self.stdout.write('\n  [1/18] Chart of Accounts...')
        coa_entries = [
            # Assets
            ('1000', 'Assets', None, 'Asset', 'Header'),
            ('1100', 'Current Assets', '1000', 'Asset', 'Header'),
            ('1110', 'Cash & Cash Equivalents', '1100', 'Asset', 'Header'),
            ('1111', 'Cash in Hand', '1110', 'Asset', 'Current Asset'),
            ('1112', 'Petty Cash', '1110', 'Asset', 'Current Asset'),
            ('1120', 'Bank Accounts', '1100', 'Asset', 'Header'),
            ('1121', 'Bank - BDT Operating Account', '1120', 'Asset', 'Current Asset'),
            ('1122', 'Bank - BDT Savings Account', '1120', 'Asset', 'Current Asset'),
            ('1123', 'Bank - GBP Account', '1120', 'Asset', 'Current Asset'),
            ('1124', 'Bank - USD Account', '1120', 'Asset', 'Current Asset'),
            ('1130', 'Receivables', '1100', 'Asset', 'Header'),
            ('1131', 'Student Fees Receivable', '1130', 'Asset', 'Current Asset'),
            ('1132', 'University Commission Receivable', '1130', 'Asset', 'Current Asset'),
            ('1140', 'Deposits & Advances', '1100', 'Asset', 'Header'),
            ('1141', 'Security Deposits', '1140', 'Asset', 'Current Asset'),
            ('1200', 'Fixed Assets', '1000', 'Asset', 'Header'),
            ('1210', 'Office Equipment', '1200', 'Asset', 'Fixed Asset'),
            ('1211', 'Accumulated Depreciation - Equipment', '1200', 'Asset', 'Fixed Asset'),
            ('1220', 'Furniture & Fixtures', '1200', 'Asset', 'Fixed Asset'),
            ('1230', 'Computers & IT Equipment', '1200', 'Asset', 'Fixed Asset'),
            # Liabilities
            ('2000', 'Liabilities', None, 'Liability', 'Header'),
            ('2100', 'Current Liabilities', '2000', 'Liability', 'Header'),
            ('2110', 'Accounts Payable', '2100', 'Liability', 'Current Liability'),
            ('2120', 'Partner Commission Payable', '2100', 'Liability', 'Current Liability'),
            ('2130', 'Accrued Liabilities', '2100', 'Liability', 'Header'),
            ('2131', 'Salary Payable', '2130', 'Liability', 'Current Liability'),
            ('2140', 'Student Advances', '2100', 'Liability', 'Header'),
            ('2141', 'Advance Fee Payments', '2140', 'Liability', 'Current Liability'),
            ('2142', 'Deferred Revenue', '2140', 'Liability', 'Current Liability'),
            ('2200', 'Long-term Liabilities', '2000', 'Liability', 'Header'),
            ('2210', 'Long-term Loans', '2200', 'Liability', 'Long-term Liability'),
            # Equity
            ('3000', 'Equity', None, 'Equity', 'Header'),
            ('3100', 'Owners Equity', '3000', 'Equity', 'Header'),
            ('3101', 'Owners Capital', '3100', 'Equity', 'Capital'),
            ('3102', 'Owners Drawings', '3100', 'Equity', 'Capital'),
            ('3200', 'Retained Earnings', '3000', 'Equity', 'Header'),
            ('3201', 'Retained Earnings', '3200', 'Equity', 'Retained Earnings'),
            ('3202', 'Current Year Profit/Loss', '3200', 'Equity', 'Retained Earnings'),
            # Income
            ('4000', 'Income', None, 'Income', 'Header'),
            ('4100', 'Fee Income', '4000', 'Income', 'Header'),
            ('4101', 'Admission Fee Income', '4100', 'Income', 'Direct Income'),
            ('4102', 'Tuition Fee Income - IFY', '4100', 'Income', 'Direct Income'),
            ('4103', 'Tuition Fee Income - IYO', '4100', 'Income', 'Direct Income'),
            ('4104', 'Tuition Fee Income - Masters Prep', '4100', 'Income', 'Direct Income'),
            ('4105', 'Visa Processing Fee Income', '4100', 'Income', 'Direct Income'),
            ('4106', 'Application Fee Income', '4100', 'Income', 'Direct Income'),
            ('4107', 'Materials & Resources Fee Income', '4100', 'Income', 'Direct Income'),
            ('4108', 'Late Fee Income', '4100', 'Income', 'Direct Income'),
            ('4109', 'Exam Fee Income', '4100', 'Income', 'Direct Income'),
            ('4110', 'Re-enrollment Fee Income', '4100', 'Income', 'Direct Income'),
            ('4200', 'Commission Income', '4000', 'Income', 'Header'),
            ('4201', 'University Commission Income', '4200', 'Income', 'Commission Income'),
            ('4300', 'Other Income', '4000', 'Income', 'Header'),
            ('4301', 'Consultation Fee Income', '4300', 'Income', 'Indirect Income'),
            ('4302', 'Interest Income', '4300', 'Income', 'Indirect Income'),
            ('4303', 'Miscellaneous Income', '4300', 'Income', 'Indirect Income'),
            # Expenses
            ('5000', 'Expenses', None, 'Expense', 'Header'),
            ('5100', 'Staff Expenses', '5000', 'Expense', 'Header'),
            ('5101', 'Salaries & Wages', '5100', 'Expense', 'Staff Expense'),
            ('5102', 'Staff Bonuses', '5100', 'Expense', 'Staff Expense'),
            ('5200', 'Occupancy Expenses', '5000', 'Expense', 'Header'),
            ('5201', 'Rent', '5200', 'Expense', 'Direct Expense'),
            ('5202', 'Electricity', '5200', 'Expense', 'Direct Expense'),
            ('5300', 'Communication & Technology', '5000', 'Expense', 'Header'),
            ('5301', 'Internet & Broadband', '5300', 'Expense', 'Indirect Expense'),
            ('5302', 'Telephone & Mobile', '5300', 'Expense', 'Indirect Expense'),
            ('5400', 'Marketing & Sales', '5000', 'Expense', 'Header'),
            ('5401', 'Advertising & Promotions', '5400', 'Expense', 'Indirect Expense'),
            ('5402', 'Event & Fair Expenses', '5400', 'Expense', 'Indirect Expense'),
            ('5403', 'Partner Commission Expense', '5400', 'Expense', 'Direct Expense'),
            ('5405', 'Marketing Materials', '5400', 'Expense', 'Indirect Expense'),
            ('5500', 'Academic Expenses', '5000', 'Expense', 'Header'),
            ('5501', 'NCUK Registration & License Fees', '5500', 'Expense', 'Direct Expense'),
            ('5503', 'Teaching Materials', '5500', 'Expense', 'Direct Expense'),
            ('5600', 'Administrative Expenses', '5000', 'Expense', 'Header'),
            ('5601', 'Office Supplies', '5600', 'Expense', 'Admin Expense'),
            ('5605', 'Bank Charges & Fees', '5600', 'Expense', 'Admin Expense'),
            ('5608', 'Miscellaneous Expense', '5600', 'Expense', 'Admin Expense'),
        ]

        coa_map = {}
        for code, name, parent, typ, sub in coa_entries:
            obj, _ = ChartOfAccount.objects.get_or_create(
                coa_code=code,
                defaults={
                    'coa_name': name,
                    'parent_code': parent,
                    'type': typ,
                    'sub_type': sub,
                    'is_system': True,
                    'is_cash_account': code in ('1111', '1112', '1121', '1122', '1123', '1124'),
                }
            )
            coa_map[code] = obj

        self.stdout.write(self.style.SUCCESS(f'  {len(coa_map)} COA accounts'))

        # ─────────────────────────────────────────────────────
        # 2. BRANCHES
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [2/18] Branches...')
        dhk, _ = Branch.objects.get_or_create(
            branch_code='DHK',
            defaults={'branch_name': 'Dhaka Branch', 'city': 'Dhaka'}
        )
        ctg, _ = Branch.objects.get_or_create(
            branch_code='CTG',
            defaults={'branch_name': 'Chattogram Branch', 'city': 'Chattogram'}
        )
        self.stdout.write(self.style.SUCCESS('  2 branches'))

        # ─────────────────────────────────────────────────────
        # 3. USERS
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [3/18] Users...')
        if not User.objects.filter(email='amran@miepathways.com').exists():
            admin = User.objects.create_superuser(
                name='Amran Hossain', email='amran@miepathways.com',
                password='MIE@2026!', role='Super Admin'
            )
        else:
            admin = User.objects.get(email='amran@miepathways.com')

        users_data = [
            ('Fatima Rahman', 'fatima@miepathways.com', 'Branch Admin', dhk),
            ('Karim Ahmed', 'karim@miepathways.com', 'Accountant', dhk),
            ('Rafiq Collector', 'rafiq@miepathways.com', 'Collector', dhk),
            ('Nadia Counselor', 'nadia@miepathways.com', 'Counselor', dhk),
            ('Zahir Chowdhury', 'zahir@miepathways.com', 'Branch Admin', ctg),
            ('Sumon Das', 'sumon@miepathways.com', 'Accountant', ctg),
            ('Bablu Collector', 'bablu@miepathways.com', 'Collector', ctg),
        ]
        user_objs = {admin.pk: admin}
        for name, email, role, branch in users_data:
            u, created = User.objects.get_or_create(
                email=email,
                defaults={'name': name, 'role': role, 'branch': branch}
            )
            if created:
                u.set_password('MIE@2026!')
                u.save()
            user_objs[u.pk] = u

        branch_admin_dhk = User.objects.get(email='fatima@miepathways.com')
        accountant_dhk = User.objects.get(email='karim@miepathways.com')
        collector_dhk = User.objects.get(email='rafiq@miepathways.com')
        branch_admin_ctg = User.objects.get(email='zahir@miepathways.com')
        accountant_ctg = User.objects.get(email='sumon@miepathways.com')
        self.stdout.write(self.style.SUCCESS(f'  {len(user_objs)} users'))

        # ─────────────────────────────────────────────────────
        # 4. PROGRAMMES
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [4/18] Programmes...')
        ify, _ = Programme.objects.get_or_create(
            code='IFY', defaults={
                'programme_name': 'International Foundation Year',
                'duration': '9 Months', 'duration_months': 9,
                'total_fee': 250000,
                'description': 'NCUK International Foundation Year'
            }
        )
        iyo, _ = Programme.objects.get_or_create(
            code='IYO', defaults={
                'programme_name': 'International Year One',
                'duration': '12 Months', 'duration_months': 12,
                'total_fee': 350000,
                'description': 'NCUK International Year One'
            }
        )
        mp, _ = Programme.objects.get_or_create(
            code='MP', defaults={
                'programme_name': 'Masters Preparation',
                'duration': '6 Months', 'duration_months': 6,
                'total_fee': 200000,
                'description': 'NCUK Masters Preparation'
            }
        )
        self.stdout.write(self.style.SUCCESS('  3 programmes'))

        # ─────────────────────────────────────────────────────
        # 5. ACADEMIC YEARS + FISCAL PERIODS
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [5/18] Academic Years & Fiscal Periods...')
        ay25, _ = AcademicYear.objects.get_or_create(
            year_name='2025-2026',
            defaults={'start_date': '2025-09-01', 'end_date': '2026-08-31'}
        )
        periods_created = 0
        pid = 1
        for month in range(9, 13):
            y, last = 2025, calendar.monthrange(2025, month)[1]
            _, created = FiscalPeriod.objects.get_or_create(
                year=ay25, period_number=month,
                defaults={
                    'period_name': date(y, month, 1).strftime('%B %Y'),
                    'start_date': f'{y}-{month:02d}-01',
                    'end_date': f'{y}-{month:02d}-{last}'
                }
            )
            if created: periods_created += 1
        for month in range(1, 9):
            y, last = 2026, calendar.monthrange(2026, month)[1]
            _, created = FiscalPeriod.objects.get_or_create(
                year=ay25, period_number=month + 4,
                defaults={
                    'period_name': date(y, month, 1).strftime('%B %Y'),
                    'start_date': f'{y}-{month:02d}-01',
                    'end_date': f'{y}-{month:02d}-{last}'
                }
            )
            if created: periods_created += 1
        self.stdout.write(self.style.SUCCESS(f'  1 year, {periods_created} periods'))

        # ─────────────────────────────────────────────────────
        # 6. EXCHANGE RATES
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [6/18] Exchange Rates...')
        rates = [
            ('GBP', 'BDT', 155.50, '2025-09-01'), ('USD', 'BDT', 121.75, '2025-09-01'),
            ('GBP', 'BDT', 157.25, '2026-01-01'), ('USD', 'BDT', 122.50, '2026-01-01'),
            ('GBP', 'BDT', 158.00, '2026-06-01'), ('USD', 'BDT', 123.00, '2026-06-01'),
        ]
        for fr, to, rate, dt in rates:
            ExchangeRate.objects.get_or_create(
                from_currency=fr, to_currency=to, effective_date=dt,
                defaults={'rate': rate, 'source': 'Bangladesh Bank'}
            )
        self.stdout.write(self.style.SUCCESS('  6 rates'))

        # ─────────────────────────────────────────────────────
        # 7. PARTNERS
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [7/18] Partners...')
        partners_data = [
            ('PNR-001', 'Global Education Services', 'Education Consultant', 'Mr. Habib',
             '+8801711100001', 'Percentage of University Commission', 15.00, None, dhk),
            ('PNR-002', 'Bright Future Consultancy', 'Agent', 'Ms. Sabrina',
             '+8801711100002', 'Percentage of University Commission', 12.00, None, ctg),
            ('PNR-003', 'StudyAbroad BD', 'Online Platform', 'Mr. Tanvir',
             '+8801711100003', 'Percentage of MIE Fee', 10.00, None, dhk),
            ('PNR-004', 'Oxford Pathway Agency', 'Agent', 'Dr. Rashid',
             '+8801711100004', 'Fixed Per Student', None, 25000, dhk),
            ('PNR-005', 'EduLink International', 'Education Consultant', 'Ms. Nasreen',
             '+8801711100005', 'Percentage of University Commission', 10.00, None, ctg),
        ]
        pnr_objs = {}
        for code, name, ptype, contact, phone, ctype, crate, camount, branch in partners_data:
            obj, _ = Partner.objects.get_or_create(
                partner_code=code,
                defaults={
                    'partner_name': name, 'partner_type': ptype,
                    'contact_person': contact, 'phone': phone,
                    'default_commission_type': ctype,
                    'default_commission_rate': crate,
                    'default_commission_amount': camount,
                    'branch': branch,
                }
            )
            pnr_objs[code] = obj
        self.stdout.write(self.style.SUCCESS('  5 partners'))

        # ─────────────────────────────────────────────────────
        # 8. UNIVERSITIES
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [8/18] Universities...')
        uni_data = [
            ('University of Birmingham', 'UK', 'Percentage of Tuition', 15.00, None, 'GBP', True),
            ('University of Leeds', 'UK', 'Percentage of Tuition', 12.50, None, 'GBP', True),
            ('University of Bristol', 'UK', 'Percentage of Tuition', 10.00, None, 'GBP', True),
            ('University of Sheffield', 'UK', 'Fixed Per Student', None, 3000, 'GBP', True),
            ('Manchester Metropolitan University', 'UK', 'Percentage of Tuition', 12.00, None, 'GBP', True),
            ('University of Auckland', 'NZ', 'Percentage of Tuition', 10.00, None, 'USD', True),
            ('University of Toronto', 'Canada', 'None', None, None, 'CAD', False),
            ('University of Sydney', 'Australia', 'Fixed Per Student', None, 2500, 'USD', True),
        ]
        uni_objs = {}
        for name, country, ctype, crate, camount, ccurr, has_comm in uni_data:
            obj, _ = University.objects.get_or_create(
                university_name=name,
                defaults={
                    'country': country, 'commission_type': ctype,
                    'commission_rate': crate, 'commission_amount': camount,
                    'commission_currency': ccurr,
                    'has_commission_agreement': has_comm,
                }
            )
            uni_objs[name] = obj
        self.stdout.write(self.style.SUCCESS('  8 universities'))

        # ─────────────────────────────────────────────────────
        # 9. PROGRAMME FEE HEADS
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [9/18] Programme Fee Heads...')
        fee_heads_data = [
            (ify, coa_map['4101'], 25000, True, False, 1),
            (ify, coa_map['4102'], 150000, True, True, 2),
            (ify, coa_map['4105'], 15000, True, False, 3),
            (ify, coa_map['4106'], 5000, True, False, 4),
            (ify, coa_map['4107'], 10000, True, False, 5),
            (ify, coa_map['4109'], 10000, True, False, 6),
            (iyo, coa_map['4101'], 30000, True, False, 1),
            (iyo, coa_map['4103'], 220000, True, True, 2),
            (iyo, coa_map['4105'], 15000, True, False, 3),
            (iyo, coa_map['4106'], 5000, True, False, 4),
            (iyo, coa_map['4107'], 12000, True, False, 5),
            (iyo, coa_map['4109'], 12000, True, False, 6),
            (mp, coa_map['4101'], 20000, True, False, 1),
            (mp, coa_map['4104'], 130000, True, True, 2),
            (mp, coa_map['4105'], 15000, True, False, 3),
            (mp, coa_map['4106'], 5000, True, False, 4),
            (mp, coa_map['4107'], 8000, True, False, 5),
        ]
        fh_count = 0
        for prog, coa, amt, mandatory, installable, order in fee_heads_data:
            _, created = ProgrammeFeeHead.objects.get_or_create(
                programme=prog, coa=coa,
                defaults={
                    'default_amount': amt, 'is_mandatory': mandatory,
                    'is_installable': installable, 'display_order': order,
                }
            )
            if created: fh_count += 1
        self.stdout.write(self.style.SUCCESS(f'  {fh_count} fee heads'))

        # ─────────────────────────────────────────────────────
        # 10. STUDENTS
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [10/18] Students...')
        students_data = [
            # (code, name, father, dob, gender, contact, email, edu, adm, prog, branch, partner, referral, status, prog_status)
            ('STU-DHK-2025-0001', 'Sakib Al Hasan', 'Mohammad Hasan', '2003-05-15', 'Male',
             '+8801711000001', 'sakib@gmail.com', 'A Level', '2025-10-01', ify, dhk,
             pnr_objs['PNR-001'], 'Partner Agent', 'Active', 'Studying'),
            ('STU-DHK-2025-0002', 'Tania Akter', 'Abdul Karim', '2004-02-20', 'Female',
             '+8801711000002', 'tania@yahoo.com', 'HSC', '2025-10-01', ify, dhk,
             pnr_objs['PNR-003'], 'Partner Agent', 'Active', 'Studying'),
            ('STU-DHK-2025-0003', 'Rafiq Ahmed', 'Late Ahmed Ali', '2003-11-10', 'Male',
             '+8801711000003', 'rafiq.ahmed@gmail.com', 'A Level', '2025-10-15', ify, dhk,
             None, 'Walk-in', 'Active', 'Studying'),
            ('STU-DHK-2025-0004', 'Farhana Islam', 'Shafiq Islam', '2004-01-05', 'Female',
             '+8801711000004', 'farhana@gmail.com', 'O Level', '2025-11-01', ify, dhk,
             None, 'Website', 'Active', 'Studying'),
            ('STU-DHK-2025-0005', 'Imran Hossain', 'Delwar Hossain', '2003-07-22', 'Male',
             '+8801711000005', 'imran.h@outlook.com', 'HSC', '2025-11-01', ify, dhk,
             pnr_objs['PNR-001'], 'Partner Agent', 'Active', 'Applying'),
            ('STU-DHK-2025-0006', 'Nusrat Jahan', 'Kamal Uddin', '2002-09-14', 'Female',
             '+8801711000006', 'nusrat.j@gmail.com', 'A Level', '2025-10-01', iyo, dhk,
             None, 'Walk-in', 'Active', 'Studying'),
            ('STU-DHK-2025-0007', 'Tanvir Rahman', 'Mostafizur Rahman', '2002-03-30', 'Male',
             '+8801711000007', 'tanvir.r@gmail.com', 'HSC', '2025-10-15', iyo, dhk,
             pnr_objs['PNR-004'], 'Partner Agent', 'Active', 'Completed'),
            ('STU-DHK-2025-0008', 'Sumaiya Khatun', 'Abdur Rahim', '2003-12-08', 'Female',
             '+8801711000008', 'sumaiya.k@gmail.com', 'A Level', '2025-11-01', iyo, dhk,
             None, 'Social Media', 'Active', 'Studying'),
            ('STU-DHK-2025-0009', 'Zahidul Islam', 'Anwar Islam', '2000-06-18', 'Male',
             '+8801711000009', 'zahid.i@gmail.com', 'Bachelor', '2025-10-01', mp, dhk,
             pnr_objs['PNR-003'], 'Partner Agent', 'Active', 'Studying'),
            ('STU-DHK-2025-0010', 'Afsana Mimi', 'Jahangir Alam', '2001-04-25', 'Female',
             '+8801711000010', 'mimi.afsana@gmail.com', 'Bachelor', '2025-10-15', mp, dhk,
             None, 'Referral', 'Active', 'Completed'),
            ('STU-CTG-2025-0001', 'Arif Chowdhury', 'Badal Chowdhury', '2004-08-12', 'Male',
             '+8801711000011', 'arif.c@gmail.com', 'O Level', '2025-10-01', ify, ctg,
             pnr_objs['PNR-002'], 'Partner Agent', 'Active', 'Studying'),
            ('STU-CTG-2025-0002', 'Mst. Rabeya', 'Abdul Gafur', '2003-10-30', 'Female',
             '+8801711000012', 'rabeya@gmail.com', 'HSC', '2025-10-15', ify, ctg,
             pnr_objs['PNR-005'], 'Partner Agent', 'Active', 'Studying'),
            ('STU-CTG-2025-0003', 'Shovon Das', 'Pranab Das', '2003-06-05', 'Male',
             '+8801711000013', 'shovon.d@gmail.com', 'A Level', '2025-11-01', ify, ctg,
             None, 'Walk-in', 'Active', 'Studying'),
            ('STU-CTG-2025-0004', 'Fatema Begum', 'Siraj Mia', '2002-01-17', 'Female',
             '+8801711000014', 'fatema.b@gmail.com', 'A Level', '2025-10-01', iyo, ctg,
             pnr_objs['PNR-002'], 'Partner Agent', 'Active', 'Offer Received'),
            ('STU-CTG-2025-0005', 'Kamrul Hasan', 'Mizanur Rahman', '2002-04-22', 'Male',
             '+8801711000015', 'kamrul.h@gmail.com', 'HSC', '2025-11-01', iyo, ctg,
             None, 'Education Fair', 'Active', 'Studying'),
            ('STU-CTG-2025-0006', 'Ruma Begum', 'Nur Hossain', '2000-09-08', 'Female',
             '+8801711000016', 'ruma.b@gmail.com', 'Bachelor', '2025-10-15', mp, ctg,
             pnr_objs['PNR-005'], 'Partner Agent', 'Completed', 'Completed'),
            ('STU-DHK-2025-0011', 'Rasel Mia', 'Jalal Mia', '2003-02-14', 'Male',
             '+8801711000017', 'rasel.m@gmail.com', 'HSC', '2025-10-01', ify, dhk,
             None, 'Walk-in', 'Dropped', 'Not Progressing'),
            ('STU-DHK-2025-0012', 'Samiha Rahman', 'Anisur Rahman', '2003-08-19', 'Female',
             '+8801711000018', 'samiha.r@gmail.com', 'A Level', '2025-10-01', iyo, dhk,
             pnr_objs['PNR-001'], 'Partner Agent', 'Active', 'Visa Process'),
            ('STU-DHK-2024-0001', 'Adnan Karim', 'Babul Karim', '2002-01-10', 'Male',
             '+8801711000019', 'adnan.k@gmail.com', 'A Level', '2024-09-01', ify, dhk,
             None, 'Walk-in', 'Completed', 'Enrolled Abroad'),
            ('STU-CTG-2024-0001', 'Maliha Sultana', 'Zahangir Alam', '2002-05-25', 'Female',
             '+8801711000020', 'maliha.s@gmail.com', 'A Level', '2024-09-01', iyo, ctg,
             pnr_objs['PNR-002'], 'Partner Agent', 'Completed', 'Enrolled Abroad'),
        ]

        student_objs = {}
        for code, name, father, dob, gender, contact, email, edu, adm, prog, branch, partner, ref, st, pst in students_data:
            obj, _ = Student.objects.get_or_create(
                student_code=code,
                defaults={
                    'full_name': name, 'father_name': father,
                    'date_of_birth': dob, 'gender': gender,
                    'contact_no': contact, 'email': email,
                    'education_qualification': edu, 'admission_date': adm,
                    'programme': prog, 'branch': branch,
                    'partner': partner, 'referral_source': ref,
                    'status': st, 'progression_status': pst,
                }
            )
            student_objs[code] = obj
        self.stdout.write(self.style.SUCCESS(f'  {len(student_objs)} students'))

        # ─────────────────────────────────────────────────────
        # 11. FEE SETUP + DUES
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [11/18] Fee Setups & Dues...')
        fees_map = {ify: (250000, 4), iyo: (350000, 4), mp: (200000, 3)}
        discounts_map = {
            'STU-DHK-2025-0001': 15000, 'STU-DHK-2025-0006': 15000,
            'STU-CTG-2025-0001': 15000,
            'STU-DHK-2025-0007': 0.10, 'STU-DHK-2025-0010': 0.10,
            'STU-CTG-2025-0006': 0.10,
        }
        fully_paid_codes = {
            'STU-DHK-2025-0007', 'STU-DHK-2025-0010', 'STU-CTG-2025-0006',
            'STU-DHK-2024-0001', 'STU-CTG-2024-0001'
        }
        partial_codes = {'STU-DHK-2025-0003', 'STU-DHK-2025-0008', 'STU-CTG-2025-0003'}
        setup_count = 0
        due_count = 0

        for code, student in student_objs.items():
            prog = student.programme
            total, inst_count = fees_map[prog]
            disc_val = discounts_map.get(code, 0)

            if isinstance(disc_val, float):
                disc_amt = int(total * disc_val)
                disc_type = 'Percentage'
            else:
                disc_amt = disc_val
                disc_type = 'Fixed' if disc_val > 0 else None

            net = total - disc_amt

            setup, _ = StudentFeeSetup.objects.get_or_create(
                student=student,
                defaults={
                    'programme': prog, 'total_programme_fee': total,
                    'discount_amount': disc_amt,
                    'discount_type': disc_type,
                    'net_payable': net, 'installment_count': inst_count,
                    'first_installment_date': student.admission_date,
                    'branch': student.branch,
                }
            )
            setup_count += 1

            inst_amt = round(net / inst_count)

            # Create tuition installment dues
            for i in range(inst_count):
                due_dt = date.fromisoformat(str(student.admission_date)) + timedelta(days=30 * i)

                if student.status == 'Dropped' and i > 0:
                    st, paid = 'Waived', 0
                elif code in fully_paid_codes:
                    st, paid = 'Paid', inst_amt
                elif code in partial_codes:
                    if i < 2:
                        st, paid = 'Paid', inst_amt
                    elif i == 2:
                        st, paid = 'Partial', round(inst_amt * 0.5)
                    else:
                        st, paid = 'Unpaid', 0
                elif i == 0:
                    st, paid = 'Paid', inst_amt
                elif i == 1 and code not in ('STU-DHK-2025-0008', 'STU-DHK-2025-0005'):
                    st, paid = 'Paid', inst_amt
                else:
                    st = 'Overdue' if due_dt < date.today() else 'Unpaid'
                    paid = 0

                tuition_coa = {'IFY': '4102', 'IYO': '4103', 'MP': '4104'}[prog.code]

                StudentDue.objects.get_or_create(
                    student=student, coa=coa_map[tuition_coa],
                    installment_no=i + 1,
                    defaults={
                        'due_date': due_dt, 'amount': inst_amt,
                        'paid_amount': paid, 'due_amount': inst_amt - paid,
                        'status': st, 'branch': student.branch,
                    }
                )
                due_count += 1

        self.stdout.write(self.style.SUCCESS(f'  {setup_count} setups, {due_count} dues'))

        # ─────────────────────────────────────────────────────
        # 12-13. PAYMENTS + LEDGER
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [12/18] Payments & Ledger...')
        pay_count = 0
        ledger_count = 0

        for code, student in student_objs.items():
            dues = StudentDue.objects.filter(
                student=student, status__in=['Paid', 'Partial']
            )
            for due in dues:
                if due.paid_amount <= 0:
                    continue

                year = due.due_date.year
                branch_code = student.branch.branch_code
                pay_count += 1
                receipt = f"MIE-{branch_code}-{year}-{pay_count:04d}"

                method = random.choice(['Cash', 'Bank Transfer', 'Mobile Banking'])

                pay_obj = Payment.objects.create(
                    receipt_no=receipt, student=student,
                    date=due.due_date, total_amount=due.paid_amount,
                    amount_in_bdt=due.paid_amount,
                    payment_method=method,
                    collected_by=collector_dhk if student.branch == dhk else accountant_ctg,
                    approved_by=branch_admin_dhk if student.branch == dhk else branch_admin_ctg,
                    approved_date=due.due_date,
                    status='Approved', branch=student.branch,
                )

                PaymentItem.objects.create(
                    payment=pay_obj, coa=due.coa,
                    amount=due.paid_amount, due=due,
                )

                # Main ledger: DR bank, CR income
                MainLedger.objects.create(
                    entry_date=due.due_date, coa=coa_map['1121'],
                    description=f'Payment {receipt}',
                    debit=due.paid_amount, credit=0,
                    reference_type='Payment', reference_id=pay_obj.pk,
                    student=student, branch=student.branch,
                )
                ledger_count += 1

                MainLedger.objects.create(
                    entry_date=due.due_date, coa=due.coa,
                    description=f'Fee income {receipt}',
                    debit=0, credit=due.paid_amount,
                    reference_type='Payment', reference_id=pay_obj.pk,
                    student=student, branch=student.branch,
                )
                ledger_count += 1

                # Student ledger
                StudentLedger.objects.create(
                    student=student, entry_date=due.due_date,
                    particulars=f'Payment received - {receipt}',
                    debit=0, credit=due.paid_amount,
                    branch=student.branch,
                )

        self.stdout.write(self.style.SUCCESS(f'  {pay_count} payments, {ledger_count} ledger'))

        # ─────────────────────────────────────────────────────
        # 14. EXPENSE VOUCHERS
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [13/18] Expense Vouchers...')
        voucher_count = 0

        expenses = [
            ('2025-10-05', 'Staff salaries - October 2025',
             [(coa_map['5101'], 180000, 0), (coa_map['5101'], 120000, 0),
              (coa_map['1121'], 0, 180000), (coa_map['1121'], 0, 120000)]),
            ('2025-10-10', 'Office rent - October 2025',
             [(coa_map['5201'], 65000, 0), (coa_map['5201'], 45000, 0),
              (coa_map['1121'], 0, 65000), (coa_map['1121'], 0, 45000)]),
            ('2025-10-15', 'NCUK annual registration fee',
             [(coa_map['5501'], 250000, 0), (coa_map['1123'], 0, 1608)]),
            ('2025-10-20', 'Marketing - Facebook ads + flyers',
             [(coa_map['5401'], 35000, 0), (coa_map['5405'], 15000, 0),
              (coa_map['1111'], 0, 50000)]),
            ('2025-11-05', 'Staff salaries - November 2025',
             [(coa_map['5101'], 180000, 0), (coa_map['5101'], 120000, 0),
              (coa_map['1121'], 0, 180000), (coa_map['1121'], 0, 120000)]),
            ('2025-12-05', 'Staff salaries - December 2025',
             [(coa_map['5101'], 180000, 0), (coa_map['5101'], 120000, 0),
              (coa_map['1121'], 0, 180000), (coa_map['1121'], 0, 120000)]),
            ('2026-01-05', 'Staff salaries - January 2026',
             [(coa_map['5101'], 190000, 0), (coa_map['5101'], 125000, 0),
              (coa_map['1121'], 0, 190000), (coa_map['1121'], 0, 125000)]),
            ('2026-02-05', 'Staff salaries - February 2026',
             [(coa_map['5101'], 190000, 0), (coa_map['5101'], 125000, 0),
              (coa_map['1121'], 0, 190000), (coa_map['1121'], 0, 125000)]),
            ('2026-03-05', 'Staff salaries - March 2026',
             [(coa_map['5101'], 190000, 0), (coa_map['5101'], 125000, 0),
              (coa_map['1121'], 0, 190000), (coa_map['1121'], 0, 125000)]),
            ('2026-03-15', 'Education fair materials',
             [(coa_map['5402'], 45000, 0), (coa_map['5405'], 20000, 0),
              (coa_map['1111'], 0, 65000)]),
            ('2026-04-05', 'Staff salaries - April 2026',
             [(coa_map['5101'], 190000, 0), (coa_map['5101'], 125000, 0),
              (coa_map['1121'], 0, 190000), (coa_map['1121'], 0, 125000)]),
            ('2026-05-05', 'Staff salaries - May 2026',
             [(coa_map['5101'], 190000, 0), (coa_map['5101'], 125000, 0),
              (coa_map['1121'], 0, 190000), (coa_map['1121'], 0, 125000)]),
            ('2026-05-15', 'Internet + phone bills',
             [(coa_map['5301'], 14000, 0), (coa_map['5302'], 8000, 0),
              (coa_map['1111'], 0, 22000)]),
            ('2026-06-05', 'Staff salaries - June 2026',
             [(coa_map['5101'], 190000, 0), (coa_map['5101'], 125000, 0),
              (coa_map['1121'], 0, 190000), (coa_map['1121'], 0, 125000)]),
        ]

        for dt, narr, entries in expenses:
            voucher_count += 1
            total_dr = sum(e[1] for e in entries)
            vno = f"MIE-VOU-{dt[:4]}-{voucher_count:04d}"

            vou = Voucher.objects.create(
                voucher_no=vno, voucher_type='Payment',
                date=dt, narration=narr,
                total_debit=total_dr, total_credit=total_dr,
                prepared_by=accountant_dhk,
                approved_by=branch_admin_dhk, approved_date=dt,
                status='Approved', branch=dhk,
            )

            for i, (coa, dr, cr) in enumerate(entries, 1):
                VoucherEntry.objects.create(
                    voucher=vou, line_number=i, coa=coa,
                    debit=dr, credit=cr, narration=narr,
                )
                MainLedger.objects.create(
                    entry_date=dt, coa=coa,
                    description=narr, debit=dr, credit=cr,
                    reference_type='Voucher', reference_id=vou.pk,
                    voucher=vou, branch=dhk,
                )
                ledger_count += 1

        self.stdout.write(self.style.SUCCESS(f'  {voucher_count} vouchers'))

        # ─────────────────────────────────────────────────────
        # 15. PETTY CASH
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [14/18] Petty Cash...')
        petty_data = [
            ('2025-10-03', 'Office stationery', 'Office Supplies', 1200, 'Rafiq', dhk),
            ('2025-10-08', 'Courier to NCUK', 'Courier', 500, 'Office Boy', dhk),
            ('2025-11-05', 'Printer toner', 'Office Supplies', 2500, 'Rafiq', dhk),
            ('2025-12-03', 'Office supplies', 'Office Supplies', 1800, 'Rafiq', dhk),
            ('2026-01-15', 'Courier to university', 'Courier', 600, 'Rafiq', dhk),
            ('2026-03-10', 'Whiteboard markers', 'Office Supplies', 900, 'Nadia', dhk),
            ('2026-05-10', 'AC servicing', 'Repair', 3500, 'Office Boy', dhk),
            ('2025-10-05', 'Stationery CTG', 'Office Supplies', 1000, 'Bablu', ctg),
            ('2025-11-10', 'Cleaning CTG', 'Cleaning', 1200, 'Office Boy', ctg),
            ('2026-03-15', 'Chair repair CTG', 'Repair', 1800, 'Office Boy', ctg),
        ]
        for dt, purpose, cat, amt, given, branch in petty_data:
            PettyCash.objects.create(
                date=dt, purpose=purpose, category=cat, amount=amt,
                given_to=given, approved_by=branch_admin_dhk if branch == dhk else branch_admin_ctg,
                branch=branch, created_by=collector_dhk,
            )
        self.stdout.write(self.style.SUCCESS(f'  {len(petty_data)} petty cash entries'))

        # ─────────────────────────────────────────────────────
        # 16. ACADEMIC RECORDS + ATTENDANCE
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [15/18] Academics...')
        modules_map = {
            ify: [('Mathematics', 'MAT101'), ('Physics', 'PHY101'),
                  ('English', 'ENG101'), ('ICT', 'ICT101'), ('Study Skills', 'SSK101')],
            iyo: [('Advanced Mathematics', 'MAT201'), ('Engineering', 'ENG201'),
                  ('Academic English', 'ENG202'), ('Computer Science', 'CS201'),
                  ('Business Studies', 'BUS201'), ('Research Methods', 'RES201')],
            mp: [('Research Methodology', 'RES301'), ('Academic Writing', 'AWR301'),
                 ('Critical Thinking', 'CTH301'), ('Subject Module', 'SSM301')],
        }
        grade_options = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
        record_count = 0
        att_count = 0

        for code, student in student_objs.items():
            if student.status == 'Dropped':
                continue
            prog = student.programme
            for mname, mcode in modules_map.get(prog, []):
                for atype in ['Coursework', 'Exam']:
                    score = random.randint(45, 95)
                    gi = min(score // 12, 6)
                    result = 'Distinction' if score >= 70 else 'Pass'
                    AcademicRecord.objects.create(
                        student=student, programme=prog,
                        module_name=mname, module_code=mcode,
                        assessment_type=atype, score=score,
                        grade=grade_options[gi], max_score=100,
                        result=result,
                        assessment_date=date(2026, 1, 15) if atype == 'Coursework' else date(2026, 3, 15),
                        academic_year=ay25,
                        recorded_by=User.objects.get(email='nadia@miepathways.com') if student.branch == dhk else branch_admin_ctg,
                        branch=student.branch,
                    )
                    record_count += 1

            for day_off in range(0, 120, 3):
                att_date = date(2025, 10, 1) + timedelta(days=day_off)
                if att_date > date.today():
                    break
                st = random.choices(['Present', 'Absent', 'Late'], weights=[80, 10, 10])[0]
                Attendance.objects.create(
                    student=student, programme=prog,
                    attendance_date=att_date, status=st,
                    recorded_by=admin, branch=student.branch,
                )
                att_count += 1

        self.stdout.write(self.style.SUCCESS(f'  {record_count} records, {att_count} attendance'))

        # ─────────────────────────────────────────────────────
        # 17. DISCOUNTS + DOCUMENTS
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [16/18] Discounts & Documents...')
        disc_data = [
            ('STU-DHK-2025-0001', 'Early Bird', 'Fixed Amount', 15000, 15000, 'Early enrollment discount'),
            ('STU-DHK-2025-0006', 'Early Bird', 'Fixed Amount', 15000, 15000, 'Early enrollment discount'),
            ('STU-DHK-2025-0007', 'Merit Scholarship', 'Percentage', 10, 35000, 'Outstanding A-Level: 3A*'),
            ('STU-DHK-2025-0010', 'Merit Scholarship', 'Percentage', 10, 20000, 'Excellent CGPA 3.8'),
            ('STU-CTG-2025-0001', 'Early Bird', 'Fixed Amount', 15000, 15000, 'Early enrollment CTG'),
            ('STU-CTG-2025-0006', 'Merit Scholarship', 'Percentage', 10, 20000, 'First class honours'),
        ]
        for code, dtype, basis, val, calc, reason in disc_data:
            Discount.objects.create(
                student=student_objs[code], discount_type=dtype,
                discount_basis=basis, discount_value=val,
                calculated_amount=calc, reason=reason,
                approved_by=admin, approval_date='2025-10-01',
                branch=student_objs[code].branch,
            )

        doc_data = [
            ('STU-DHK-2025-0001', 'Passport'), ('STU-DHK-2025-0001', 'Transcript'),
            ('STU-DHK-2025-0002', 'National ID'), ('STU-DHK-2025-0003', 'Passport'),
            ('STU-DHK-2025-0006', 'Passport'), ('STU-DHK-2025-0007', 'Passport'),
            ('STU-DHK-2025-0007', 'Offer Letter'), ('STU-CTG-2025-0001', 'Passport'),
            ('STU-CTG-2025-0004', 'Passport'), ('STU-DHK-2024-0001', 'Passport'),
            ('STU-DHK-2024-0001', 'Visa Copy'), ('STU-CTG-2024-0001', 'Passport'),
            ('STU-CTG-2024-0001', 'Visa Copy'),
        ]
        for code, dtype in doc_data:
            StudentDocument.objects.create(
                student=student_objs[code], document_type=dtype,
                file_name=f'{code}_{dtype.lower()}.pdf',
                file_path=f'/docs/{code}/{dtype.lower()}.pdf',
                is_verified=True, branch=student_objs[code].branch,
                uploaded_by=admin,
            )
        self.stdout.write(self.style.SUCCESS(f'  {len(disc_data)} discounts, {len(doc_data)} docs'))

        # ─────────────────────────────────────────────────────
        # 18. PROGRESSION & COMMISSIONS
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [17/18] Progression & Commissions...')
        prog_data = [
            ('STU-DHK-2025-0005', 'University of Birmingham', 'BSc Computer Science',
             'UK', '2026-03-01', 'Offer Accepted', 18000, 'Applied', None, 'Not Enrolled'),
            ('STU-DHK-2025-0007', 'University of Leeds', 'BEng Mechanical Engineering',
             'UK', '2026-02-01', 'Offer Accepted', 22000, 'Granted', '2026-05-20', 'Enrolled'),
            ('STU-DHK-2025-0010', 'University of Bristol', 'MSc Data Science',
             'UK', '2026-03-15', 'Offer Accepted', 25000, 'Granted', '2026-05-25', 'Enrolled'),
            ('STU-CTG-2025-0004', 'University of Sheffield', 'BSc Business Management',
             'UK', '2026-04-01', 'Conditional Offer', 16000, 'Not Started', None, 'Not Enrolled'),
            ('STU-CTG-2025-0006', 'Manchester Metropolitan University', 'MBA',
             'UK', '2026-02-15', 'Offer Accepted', 20000, 'Granted', '2026-05-10', 'Enrolled'),
            ('STU-DHK-2024-0001', 'University of Birmingham', 'BSc Computer Science',
             'UK', '2025-04-01', 'Offer Accepted', 18000, 'Granted', '2025-07-20', 'Enrolled'),
            ('STU-CTG-2024-0001', 'University of Leeds', 'BEng Civil Engineering',
             'UK', '2025-04-15', 'Offer Accepted', 22000, 'Granted', '2025-07-25', 'Enrolled'),
            ('STU-DHK-2025-0012', 'University of Bristol', 'BSc Business Analytics',
             'UK', '2026-05-01', 'Offer Accepted', 21000, 'Applied', None, 'Not Enrolled'),
        ]

        for scode, uname, papplied, country, adate, astatus, tuition, vstatus, vdate, estatus in prog_data:
            student = student_objs[scode]
            university = uni_objs[uname]

            pr = ProgressionRecord.objects.create(
                student=student, university=university,
                programme_applied=papplied, country=country,
                application_date=adate, application_status=astatus,
                tuition_fee_at_uni=tuition,
                visa_status=vstatus, visa_grant_date=vdate,
                enrollment_status=estatus,
                enrollment_date=date(2026, 6, 1) if estatus == 'Enrolled' else None,
                commission_status='Pending' if estatus == 'Enrolled' else 'Not Applicable',
                branch=student.branch, created_by=admin,
            )

            # Create university commission for enrolled students
            if estatus == 'Enrolled' and university.has_commission_agreement:
                rate = university.commission_rate or 0
                amount_uni_comm_amount = university.commission_amount or 0
                if university.commission_type == 'Percentage of Tuition':
                    gross = float(tuition) * float(rate) / 100
                elif university.commission_type == 'Fixed Per Student':
                    gross = float(amount_uni_comm_amount)
                else:
                    gross = 0

                bdt = gross * 158.00

                uc_status = 'Received' if astatus == 'Offer Accepted' and adate < '2025-12-01' else 'Expected'

                uni_comm = UniversityCommission.objects.create(
                    progression_record=pr, university=university,
                    student=student, commission_type=university.commission_type,
                    commission_rate=rate, tuition_base=tuition,
                    gross_commission=gross, commission_in_bdt=bdt,
                    exchange_rate=158.00,
                    status=uc_status,
                    branch=student.branch, created_by=admin,
                )

                # Partner commission
                if student.partner:
                    partner = student.partner
                    if partner.default_commission_type == 'Percentage of University Commission':
                        pamt = round(bdt * float(partner.default_commission_rate or 0) / 100)
                    elif partner.default_commission_type == 'Percentage of MIE Fee':
                        pamt = round(float(student.total_paid or 0) * float(partner.default_commission_rate or 0) / 100)
                    elif partner.default_commission_type == 'Fixed Per Student':
                        pamt = float(partner.default_commission_amount or 0)
                    else:
                        pamt = 0

                    pc_status = 'Paid' if uc_status == 'Received' and scode == 'STU-CTG-2024-0001' else (
                        'Approved' if scode == 'STU-DHK-2025-0007' else 'Calculated'
                    )

                    pc = PartnerCommission.objects.create(
                        partner=partner, student=student,
                        university_commission=uni_comm,
                        commission_type=partner.default_commission_type,
                        commission_rate=partner.default_commission_rate,
                        base_amount=bdt, calculated_amount=pamt,
                        calculated_date=date.today(),
                        status=pc_status,
                        remaining_amount=0 if pc_status == 'Paid' else pamt,
                        branch=student.branch, created_by=admin,
                    )

                    if pc_status == 'Paid':
                        PartnerPayment.objects.create(
                            partner_commission=pc, partner=partner,
                            payment_date=date(2026, 6, 5),
                            amount=pamt, payment_method='Bank Transfer',
                            bank_coa=coa_map['1121'],
                            status='Completed', branch=student.branch,
                            created_by=admin, approved_by=admin,
                        )

        self.stdout.write(self.style.SUCCESS('  Progression & commissions done'))

        # ─────────────────────────────────────────────────────
        # 19. Update student financial totals
        # ─────────────────────────────────────────────────────
        self.stdout.write('  [18/18] Updating financial totals...')
        for student in Student.objects.all():
            dues = StudentDue.objects.filter(student=student)
            agg = dues.aggregate(
                total=models.Sum('amount'),
                paid=models.Sum('paid_amount'),
                due=models.Sum('due_amount'),
            )
            student.total_fee = agg['total'] or 0
            student.total_paid = agg['paid'] or 0
            student.total_due = agg['due'] or 0
            student.save(update_fields=['total_fee', 'total_paid', 'total_due'])

        # ─────────────────────────────────────────────────────
        # DONE
        # ─────────────────────────────────────────────────────
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('  ALL SEEDED VIA DJANGO ORM'))
        self.stdout.write(self.style.SUCCESS(f'  {ChartOfAccount.objects.count()} COA accounts'))
        self.stdout.write(self.style.SUCCESS(f'  {Student.objects.count()} students'))
        self.stdout.write(self.style.SUCCESS(f'  {Payment.objects.count()} payments'))
        self.stdout.write(self.style.SUCCESS(f'  {Voucher.objects.count()} vouchers'))
        self.stdout.write(self.style.SUCCESS(f'  {MainLedger.objects.count()} ledger entries'))
        self.stdout.write(self.style.SUCCESS(f'  {StudentDue.objects.count()} due records'))
        self.stdout.write(self.style.SUCCESS(f'  {ProgressionRecord.objects.count()} progressions'))
        self.stdout.write(self.style.WARNING('=' * 60))