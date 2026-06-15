import random
import calendar
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Seed all tables with realistic demo data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('  MIE PATHWAYS — FULL DATA SEED'))
        self.stdout.write(self.style.WARNING('=' * 60))

        c = connection.cursor()

        # ────────────────────────────────────────────────────────
        # 0. Clear ALL data
        # ────────────────────────────────────────────────────────
        self.stdout.write('\n  Clearing ALL data...')
        c.execute("SET FOREIGN_KEY_CHECKS = 0")
        tables_to_clear = [
            'partner_payments', 'partner_commissions',
            'university_commissions', 'progression_records',
            'late_fee_charges', 'petty_cash', 'financial_snapshots',
            'notifications', 'student_ledger', 'main_ledger',
            'voucher_entries', 'vouchers', 'payment_items', 'payments',
            'attendance', 'academic_records', 'student_documents',
            'discounts', 'student_dues', 'student_fee_setup',
            'students', 'programme_fee_heads', 'fiscal_periods',
            'academic_years', 'universities', 'partners',
            'exchange_rates', 'programmes', 'audit_log',
        ]
        for table in tables_to_clear:
            try:
                c.execute(f"TRUNCATE TABLE {table}")
            except Exception:
                pass
        c.execute("SET FOREIGN_KEY_CHECKS = 1")
        self.stdout.write(self.style.SUCCESS('  Cleared'))

                # ────────────────────────────────────────────────────────
        # 0b. Seed Chart of Accounts if empty
        # ────────────────────────────────────────────────────────
        c.execute("SELECT COUNT(*) FROM chart_of_accounts")
        coa_count = c.fetchone()[0]

        if coa_count == 0:
            self.stdout.write('  Seeding Chart of Accounts...')
            coa_data = [
                ('1000', 'Assets', None, 'Asset', 'Header', 1, 0),
                ('1100', 'Current Assets', '1000', 'Asset', 'Header', 1, 0),
                ('1110', 'Cash & Cash Equivalents', '1100', 'Asset', 'Header', 1, 1),
                ('1111', 'Cash in Hand', '1110', 'Asset', 'Current Asset', 1, 1),
                ('1112', 'Petty Cash', '1110', 'Asset', 'Current Asset', 1, 1),
                ('1120', 'Bank Accounts', '1100', 'Asset', 'Header', 1, 1),
                ('1121', 'Bank - BDT Operating Account', '1120', 'Asset', 'Current Asset', 1, 1),
                ('1122', 'Bank - BDT Savings Account', '1120', 'Asset', 'Current Asset', 1, 1),
                ('1123', 'Bank - GBP Account', '1120', 'Asset', 'Current Asset', 1, 1),
                ('1124', 'Bank - USD Account', '1120', 'Asset', 'Current Asset', 1, 1),
                ('1130', 'Receivables', '1100', 'Asset', 'Header', 1, 0),
                ('1131', 'Student Fees Receivable', '1130', 'Asset', 'Current Asset', 1, 0),
                ('1132', 'University Commission Receivable', '1130', 'Asset', 'Current Asset', 1, 0),
                ('1133', 'Other Receivables', '1130', 'Asset', 'Current Asset', 0, 0),
                ('1140', 'Deposits & Advances', '1100', 'Asset', 'Header', 1, 0),
                ('1141', 'Security Deposits', '1140', 'Asset', 'Current Asset', 1, 0),
                ('1142', 'Prepaid Rent', '1140', 'Asset', 'Current Asset', 0, 0),
                ('1143', 'Advance Payments', '1140', 'Asset', 'Current Asset', 0, 0),
                ('1200', 'Fixed Assets', '1000', 'Asset', 'Header', 1, 0),
                ('1210', 'Office Equipment', '1200', 'Asset', 'Fixed Asset', 0, 0),
                ('1211', 'Accumulated Depreciation - Equipment', '1200', 'Asset', 'Fixed Asset', 0, 0),
                ('1220', 'Furniture & Fixtures', '1200', 'Asset', 'Fixed Asset', 0, 0),
                ('1221', 'Accumulated Depreciation - Furniture', '1200', 'Asset', 'Fixed Asset', 0, 0),
                ('1230', 'Computers & IT Equipment', '1200', 'Asset', 'Fixed Asset', 0, 0),
                ('1231', 'Accumulated Depreciation - Computers', '1200', 'Asset', 'Fixed Asset', 0, 0),
                ('2000', 'Liabilities', None, 'Liability', 'Header', 1, 0),
                ('2100', 'Current Liabilities', '2000', 'Liability', 'Header', 1, 0),
                ('2110', 'Accounts Payable', '2100', 'Liability', 'Current Liability', 1, 0),
                ('2120', 'Partner Commission Payable', '2100', 'Liability', 'Current Liability', 1, 0),
                ('2130', 'Accrued Liabilities', '2100', 'Liability', 'Header', 1, 0),
                ('2131', 'Salary Payable', '2130', 'Liability', 'Current Liability', 0, 0),
                ('2132', 'Tax Payable', '2130', 'Liability', 'Current Liability', 0, 0),
                ('2133', 'Utilities Payable', '2130', 'Liability', 'Current Liability', 0, 0),
                ('2140', 'Student Advances', '2100', 'Liability', 'Header', 1, 0),
                ('2141', 'Advance Fee Payments', '2140', 'Liability', 'Current Liability', 1, 0),
                ('2142', 'Deferred Revenue', '2140', 'Liability', 'Current Liability', 1, 0),
                ('2200', 'Long-term Liabilities', '2000', 'Liability', 'Header', 1, 0),
                ('2210', 'Long-term Loans', '2200', 'Liability', 'Long-term Liability', 0, 0),
                ('3000', 'Equity', None, 'Equity', 'Header', 1, 0),
                ('3100', 'Owners Equity', '3000', 'Equity', 'Header', 1, 0),
                ('3101', 'Owners Capital', '3100', 'Equity', 'Capital', 1, 0),
                ('3102', 'Owners Drawings', '3100', 'Equity', 'Capital', 1, 0),
                ('3200', 'Retained Earnings', '3000', 'Equity', 'Header', 1, 0),
                ('3201', 'Retained Earnings', '3200', 'Equity', 'Retained Earnings', 1, 0),
                ('3202', 'Current Year Profit/Loss', '3200', 'Equity', 'Retained Earnings', 1, 0),
                ('4000', 'Income', None, 'Income', 'Header', 1, 0),
                ('4100', 'Fee Income', '4000', 'Income', 'Header', 1, 0),
                ('4101', 'Admission Fee Income', '4100', 'Income', 'Direct Income', 1, 0),
                ('4102', 'Tuition Fee Income - IFY', '4100', 'Income', 'Direct Income', 1, 0),
                ('4103', 'Tuition Fee Income - IYO', '4100', 'Income', 'Direct Income', 1, 0),
                ('4104', 'Tuition Fee Income - Masters Prep', '4100', 'Income', 'Direct Income', 1, 0),
                ('4105', 'Visa Processing Fee Income', '4100', 'Income', 'Direct Income', 1, 0),
                ('4106', 'Application Fee Income', '4100', 'Income', 'Direct Income', 1, 0),
                ('4107', 'Materials & Resources Fee Income', '4100', 'Income', 'Direct Income', 1, 0),
                ('4108', 'Late Fee Income', '4100', 'Income', 'Direct Income', 1, 0),
                ('4109', 'Exam Fee Income', '4100', 'Income', 'Direct Income', 1, 0),
                ('4110', 'Re-enrollment Fee Income', '4100', 'Income', 'Direct Income', 1, 0),
                ('4200', 'Commission Income', '4000', 'Income', 'Header', 1, 0),
                ('4201', 'University Commission Income', '4200', 'Income', 'Commission Income', 1, 0),
                ('4202', 'Bonus & Incentive Income', '4200', 'Income', 'Commission Income', 1, 0),
                ('4300', 'Other Income', '4000', 'Income', 'Header', 1, 0),
                ('4301', 'Consultation Fee Income', '4300', 'Income', 'Indirect Income', 0, 0),
                ('4302', 'Interest Income', '4300', 'Income', 'Indirect Income', 0, 0),
                ('4303', 'Miscellaneous Income', '4300', 'Income', 'Indirect Income', 0, 0),
                ('5000', 'Expenses', None, 'Expense', 'Header', 1, 0),
                ('5100', 'Staff Expenses', '5000', 'Expense', 'Header', 1, 0),
                ('5101', 'Salaries & Wages', '5100', 'Expense', 'Staff Expense', 1, 0),
                ('5102', 'Staff Bonuses', '5100', 'Expense', 'Staff Expense', 0, 0),
                ('5103', 'Staff Benefits & Allowances', '5100', 'Expense', 'Staff Expense', 0, 0),
                ('5104', 'Overtime Pay', '5100', 'Expense', 'Staff Expense', 0, 0),
                ('5105', 'Training & Development', '5100', 'Expense', 'Staff Expense', 0, 0),
                ('5200', 'Occupancy Expenses', '5000', 'Expense', 'Header', 1, 0),
                ('5201', 'Rent', '5200', 'Expense', 'Direct Expense', 1, 0),
                ('5202', 'Electricity', '5200', 'Expense', 'Direct Expense', 0, 0),
                ('5203', 'Gas', '5200', 'Expense', 'Direct Expense', 0, 0),
                ('5204', 'Water', '5200', 'Expense', 'Direct Expense', 0, 0),
                ('5205', 'Maintenance & Repairs', '5200', 'Expense', 'Direct Expense', 0, 0),
                ('5206', 'Security Services', '5200', 'Expense', 'Direct Expense', 0, 0),
                ('5207', 'Cleaning Services', '5200', 'Expense', 'Direct Expense', 0, 0),
                ('5300', 'Communication & Technology', '5000', 'Expense', 'Header', 1, 0),
                ('5301', 'Internet & Broadband', '5300', 'Expense', 'Indirect Expense', 0, 0),
                ('5302', 'Telephone & Mobile', '5300', 'Expense', 'Indirect Expense', 0, 0),
                ('5303', 'Software & Subscriptions', '5300', 'Expense', 'Indirect Expense', 0, 0),
                ('5304', 'IT Support & Maintenance', '5300', 'Expense', 'Indirect Expense', 0, 0),
                ('5400', 'Marketing & Sales', '5000', 'Expense', 'Header', 1, 0),
                ('5401', 'Advertising & Promotions', '5400', 'Expense', 'Indirect Expense', 0, 0),
                ('5402', 'Event & Fair Expenses', '5400', 'Expense', 'Indirect Expense', 0, 0),
                ('5403', 'Partner Commission Expense', '5400', 'Expense', 'Direct Expense', 1, 0),
                ('5404', 'Referral Bonus', '5400', 'Expense', 'Indirect Expense', 0, 0),
                ('5405', 'Marketing Materials', '5400', 'Expense', 'Indirect Expense', 0, 0),
                ('5500', 'Academic Expenses', '5000', 'Expense', 'Header', 1, 0),
                ('5501', 'NCUK Registration & License Fees', '5500', 'Expense', 'Direct Expense', 1, 0),
                ('5502', 'Examination Fees', '5500', 'Expense', 'Direct Expense', 0, 0),
                ('5503', 'Teaching Materials', '5500', 'Expense', 'Direct Expense', 0, 0),
                ('5504', 'Library & Resources', '5500', 'Expense', 'Direct Expense', 0, 0),
                ('5505', 'Guest Lecturer Fees', '5500', 'Expense', 'Direct Expense', 0, 0),
                ('5506', 'Student Activities', '5500', 'Expense', 'Direct Expense', 0, 0),
                ('5600', 'Administrative Expenses', '5000', 'Expense', 'Header', 1, 0),
                ('5601', 'Office Supplies', '5600', 'Expense', 'Admin Expense', 0, 0),
                ('5602', 'Printing & Stationery', '5600', 'Expense', 'Admin Expense', 0, 0),
                ('5603', 'Travel & Transport', '5600', 'Expense', 'Admin Expense', 0, 0),
                ('5604', 'Legal & Professional Fees', '5600', 'Expense', 'Admin Expense', 0, 0),
                ('5605', 'Bank Charges & Fees', '5600', 'Expense', 'Admin Expense', 1, 0),
                ('5606', 'Insurance', '5600', 'Expense', 'Admin Expense', 0, 0),
                ('5607', 'Postage & Courier', '5600', 'Expense', 'Admin Expense', 0, 0),
                ('5608', 'Miscellaneous Expense', '5600', 'Expense', 'Admin Expense', 0, 0),
                ('5700', 'Depreciation', '5000', 'Expense', 'Header', 1, 0),
                ('5701', 'Depreciation - Equipment', '5700', 'Expense', 'Indirect Expense', 0, 0),
                ('5702', 'Depreciation - Furniture', '5700', 'Expense', 'Indirect Expense', 0, 0),
                ('5703', 'Depreciation - Computers', '5700', 'Expense', 'Indirect Expense', 0, 0),
            ]
            for entry in coa_data:
                c.execute(
                    "INSERT INTO chart_of_accounts (coa_code, coa_name, parent_code, type, "
                    "sub_type, is_system, is_cash_account) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    entry
                )
            self.stdout.write(self.style.SUCCESS(f'  {len(coa_data)} COA accounts seeded'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  COA already has {coa_count} accounts'))


        # ────────────────────────────────────────────────────────
        # Build COA lookup dict: code → actual coa_id
        # ────────────────────────────────────────────────────────
        c.execute("SELECT coa_id, coa_code FROM chart_of_accounts")
        COA = {row[1]: row[0] for row in c.fetchall()}
        self.stdout.write(self.style.SUCCESS(
            f'  COA lookup built: {len(COA)} accounts mapped'
        ))



        # ────────────────────────────────────────────────────────
        # 1. PROGRAMMES
        # ────────────────────────────────────────────────────────
        self.stdout.write('\n  [1/18] Programmes...')
        programmes = [
            (1, 'International Foundation Year', 'IFY', '9 Months', 9, 250000, 'BDT',
             'NCUK International Foundation Year programme preparing students for undergraduate entry to UK universities.'),
            (2, 'International Year One', 'IYO', '12 Months', 12, 350000, 'BDT',
             'NCUK International Year One — direct entry to second year of undergraduate degree.'),
            (3, 'Masters Preparation', 'MP', '6 Months', 6, 200000, 'BDT',
             'NCUK Masters Preparation programme for postgraduate entry.'),
        ]
        for p in programmes:
            c.execute(
                "INSERT INTO programmes (programme_id, programme_name, code, duration, "
                "duration_months, total_fee, currency, description, status, branch_id) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'Active',NULL)", p
            )
        self.stdout.write(self.style.SUCCESS('  3 programmes'))

        # ────────────────────────────────────────────────────────
        # 2. ACADEMIC YEARS
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [2/18] Academic Years...')
        c.execute(
            "INSERT INTO academic_years (year_id, year_name, start_date, end_date, status) "
            "VALUES (1, '2025-2026', '2025-09-01', '2026-08-31', 'Active')"
        )
        c.execute(
            "INSERT INTO academic_years (year_id, year_name, start_date, end_date, status) "
            "VALUES (2, '2026-2027', '2026-09-01', '2027-08-31', 'Active')"
        )
        self.stdout.write(self.style.SUCCESS('  2 academic years'))

        # ────────────────────────────────────────────────────────
        # 3. FISCAL PERIODS
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [3/18] Fiscal Periods...')
        pid = 1
        for month in range(9, 13):
            y = 2025
            last_day = calendar.monthrange(y, month)[1]
            name = date(y, month, 1).strftime('%B %Y')
            c.execute(
                "INSERT INTO fiscal_periods (period_id, year_id, period_name, period_number, "
                "start_date, end_date) VALUES (%s,1,%s,%s,%s,%s)",
                (pid, name, month, f'{y}-{month:02d}-01', f'{y}-{month:02d}-{last_day}')
            )
            pid += 1
        for month in range(1, 9):
            y = 2026
            last_day = calendar.monthrange(y, month)[1]
            name = date(y, month, 1).strftime('%B %Y')
            c.execute(
                "INSERT INTO fiscal_periods (period_id, year_id, period_name, period_number, "
                "start_date, end_date) VALUES (%s,1,%s,%s,%s,%s)",
                (pid, name, month + 4, f'{y}-{month:02d}-01', f'{y}-{month:02d}-{last_day}')
            )
            pid += 1
        self.stdout.write(self.style.SUCCESS(f'  {pid - 1} fiscal periods'))

        # ────────────────────────────────────────────────────────
        # 4. EXCHANGE RATES
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [4/18] Exchange Rates...')
        rates = [
            ('GBP', 'BDT', 155.50, '2025-09-01'), ('USD', 'BDT', 121.75, '2025-09-01'),
            ('GBP', 'BDT', 157.25, '2026-01-01'), ('USD', 'BDT', 122.50, '2026-01-01'),
            ('GBP', 'BDT', 158.00, '2026-06-01'), ('USD', 'BDT', 123.00, '2026-06-01'),
        ]
        for i, r in enumerate(rates, 1):
            c.execute(
                "INSERT INTO exchange_rates (rate_id, from_currency, to_currency, rate, "
                "effective_date, source) VALUES (%s,%s,%s,%s,%s,'Bangladesh Bank')",
                (i, *r)
            )
        self.stdout.write(self.style.SUCCESS('  6 exchange rates'))

        # ────────────────────────────────────────────────────────
        # 5. PARTNERS
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [5/18] Partners...')
        partners = [
            (1, 'PNR-001', 'Global Education Services', 'Education Consultant',
             'Mr. Habib', '+8801711100001', 'habib@globaledu.com', 'Gulshan, Dhaka', 'Dhaka',
             'Percentage of University Commission', 15.00, None, 'BDT', 30, 1),
            (2, 'PNR-002', 'Bright Future Consultancy', 'Agent',
             'Ms. Sabrina', '+8801711100002', 'sabrina@brightfuture.com', 'Agrabad, Chattogram', 'Chattogram',
             'Percentage of University Commission', 12.00, None, 'BDT', 30, 2),
            (3, 'PNR-003', 'StudyAbroad BD', 'Online Platform',
             'Mr. Tanvir', '+8801711100003', 'tanvir@studyabroadbd.com', 'Dhanmondi, Dhaka', 'Dhaka',
             'Percentage of MIE Fee', 10.00, None, 'BDT', 45, 1),
            (4, 'PNR-004', 'Oxford Pathway Agency', 'Agent',
             'Dr. Rashid', '+8801711100004', 'rashid@oxfordpath.com', 'Motijheel, Dhaka', 'Dhaka',
             'Fixed Per Student', None, 25000, 'BDT', 30, 1),
            (5, 'PNR-005', 'EduLink International', 'Education Consultant',
             'Ms. Nasreen', '+8801711100005', 'nasreen@edulink.com', 'Nasirabad, Chattogram', 'Chattogram',
             'Percentage of University Commission', 10.00, None, 'BDT', 30, 2),
        ]
        for p in partners:
            c.execute(
                "INSERT INTO partners (partner_id, partner_code, partner_name, partner_type, "
                "contact_person, phone, email, address, city, "
                "default_commission_type, default_commission_rate, default_commission_amount, "
                "payment_currency, payment_terms_days, branch_id) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", p
            )
        self.stdout.write(self.style.SUCCESS('  5 partners'))

        # ────────────────────────────────────────────────────────
        # 6. UNIVERSITIES
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [6/18] Universities...')
        universities = [
            (1, 'University of Birmingham', 'United Kingdom', 'Birmingham', 'Top 100',
             1, 'Percentage of Tuition', 15.00, None, 'GBP',
             'After enrollment confirmation', 'Admissions Office', 'admit@bham.ac.uk'),
            (2, 'University of Leeds', 'United Kingdom', 'Leeds', 'Top 100',
             1, 'Percentage of Tuition', 12.50, None, 'GBP',
             'After enrollment confirmation', 'Int''l Office', 'intl@leeds.ac.uk'),
            (3, 'University of Bristol', 'United Kingdom', 'Bristol', 'Top 50',
             1, 'Percentage of Tuition', 10.00, None, 'GBP',
             'After enrollment confirmation', 'Partnerships', 'partners@bristol.ac.uk'),
            (4, 'University of Sheffield', 'United Kingdom', 'Sheffield', 'Top 100',
             1, 'Fixed Per Student', None, 3000, 'GBP',
             'After enrollment confirmation', 'Student Recruitment', 'recruit@sheffield.ac.uk'),
            (5, 'Manchester Metropolitan University', 'United Kingdom', 'Manchester', 'Top 200',
             1, 'Percentage of Tuition', 12.00, None, 'GBP',
             'After enrollment confirmation', 'Int''l Office', 'intl@mmu.ac.uk'),
            (6, 'University of Auckland', 'New Zealand', 'Auckland', 'Top 100',
             1, 'Percentage of Tuition', 10.00, None, 'USD',
             'After first semester', 'Int''l Admissions', 'intladm@auckland.ac.nz'),
            (7, 'University of Toronto', 'Canada', 'Toronto', 'Top 20',
             0, 'None', None, None, 'CAD', None, None, None),
            (8, 'University of Sydney', 'Australia', 'Sydney', 'Top 50',
             1, 'Fixed Per Student', None, 2500, 'USD',
             'After census date', 'Agent Manager', 'agents@sydney.edu.au'),
        ]
        for u in universities:
            c.execute(
                "INSERT INTO universities (university_id, university_name, country, city, "
                "ranking, has_commission_agreement, commission_type, commission_rate, "
                "commission_amount, commission_currency, commission_payment_terms, "
                "contact_person, contact_email) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", u
            )
        self.stdout.write(self.style.SUCCESS('  8 universities'))

        # ────────────────────────────────────────────────────────
        # 7. PROGRAMME FEE HEADS (using COA dict)
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [7/18] Programme Fee Heads...')
        fee_heads = [
            (1, COA['4101'], 25000, 1, 0, 1),
            (1, COA['4102'], 150000, 1, 1, 2),
            (1, COA['4105'], 15000, 1, 0, 3),
            (1, COA['4106'], 5000, 1, 0, 4),
            (1, COA['4107'], 10000, 1, 0, 5),
            (1, COA['4109'], 10000, 1, 0, 6),
            (2, COA['4101'], 30000, 1, 0, 1),
            (2, COA['4103'], 220000, 1, 1, 2),
            (2, COA['4105'], 15000, 1, 0, 3),
            (2, COA['4106'], 5000, 1, 0, 4),
            (2, COA['4107'], 12000, 1, 0, 5),
            (2, COA['4109'], 12000, 1, 0, 6),
            (3, COA['4101'], 20000, 1, 0, 1),
            (3, COA['4104'], 130000, 1, 1, 2),
            (3, COA['4105'], 15000, 1, 0, 3),
            (3, COA['4106'], 5000, 1, 0, 4),
            (3, COA['4107'], 8000, 1, 0, 5),
        ]
        for fh in fee_heads:
            c.execute(
                "INSERT INTO programme_fee_heads (programme_id, coa_id, default_amount, "
                "is_mandatory, is_installable, display_order) VALUES (%s,%s,%s,%s,%s,%s)", fh
            )
        self.stdout.write(self.style.SUCCESS(f'  {len(fee_heads)} fee heads'))

        # ────────────────────────────────────────────────────────
        # 8. STUDENTS
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [8/18] Students...')
        students = [
            (1, 'STU-DHK-2025-0001', 'Sakib Al Hasan', 'Mohammad Hasan', 'Fatema Hasan',
             '2003-05-15', 'Male', '1999501234', 'A1234567', '+8801711000001',
             'sakib@gmail.com', 'A Level', '2025-10-01', 1, 1, 1, 'Partner Agent', 'Active', 'Studying'),
            (2, 'STU-DHK-2025-0002', 'Tania Akter', 'Abdul Karim', 'Roksana Karim',
             '2004-02-20', 'Female', '1999602345', 'B2345678', '+8801711000002',
             'tania@yahoo.com', 'HSC', '2025-10-01', 1, 1, 3, 'Partner Agent', 'Active', 'Studying'),
            (3, 'STU-DHK-2025-0003', 'Rafiq Ahmed', 'Late Ahmed Ali', 'Shahana Begum',
             '2003-11-10', 'Male', '1999703456', 'C3456789', '+8801711000003',
             'rafiq.ahmed@gmail.com', 'A Level', '2025-10-15', 1, 1, None, 'Walk-in', 'Active', 'Studying'),
            (4, 'STU-DHK-2025-0004', 'Farhana Islam', 'Shafiq Islam', 'Nasreen Islam',
             '2004-01-05', 'Female', '1999804567', 'D4567890', '+8801711000004',
             'farhana@gmail.com', 'O Level', '2025-11-01', 1, 1, None, 'Website', 'Active', 'Studying'),
            (5, 'STU-DHK-2025-0005', 'Imran Hossain', 'Delwar Hossain', 'Amena Hossain',
             '2003-07-22', 'Male', '1999905678', 'E5678901', '+8801711000005',
             'imran.h@outlook.com', 'HSC', '2025-11-01', 1, 1, 1, 'Partner Agent', 'Active', 'Applying'),
            (6, 'STU-DHK-2025-0006', 'Nusrat Jahan', 'Kamal Uddin', 'Shahana Uddin',
             '2002-09-14', 'Female', '1999506789', 'F6789012', '+8801711000006',
             'nusrat.j@gmail.com', 'A Level', '2025-10-01', 2, 1, None, 'Walk-in', 'Active', 'Studying'),
            (7, 'STU-DHK-2025-0007', 'Tanvir Rahman', 'Mostafizur Rahman', 'Shirin Rahman',
             '2002-03-30', 'Male', '1999507890', 'G7890123', '+8801711000007',
             'tanvir.r@gmail.com', 'HSC', '2025-10-15', 2, 1, 4, 'Partner Agent', 'Active', 'Completed'),
            (8, 'STU-DHK-2025-0008', 'Sumaiya Khatun', 'Abdur Rahim', 'Monowara Khatun',
             '2003-12-08', 'Female', '1999508901', 'H8901234', '+8801711000008',
             'sumaiya.k@gmail.com', 'A Level', '2025-11-01', 2, 1, None, 'Social Media', 'Active', 'Studying'),
            (9, 'STU-DHK-2025-0009', 'Zahidul Islam', 'Anwar Islam', 'Rahela Islam',
             '2000-06-18', 'Male', '1996509012', 'I9012345', '+8801711000009',
             'zahid.i@gmail.com', 'Bachelor', '2025-10-01', 3, 1, 3, 'Partner Agent', 'Active', 'Studying'),
            (10, 'STU-DHK-2025-0010', 'Afsana Mimi', 'Jahangir Alam', 'Shahida Alam',
             '2001-04-25', 'Female', '1997600123', 'J0123456', '+8801711000010',
             'mimi.afsana@gmail.com', 'Bachelor', '2025-10-15', 3, 1, None, 'Referral', 'Active', 'Completed'),
            (11, 'STU-CTG-2025-0001', 'Arif Chowdhury', 'Badal Chowdhury', 'Rina Chowdhury',
             '2004-08-12', 'Male', '1999501111', 'K1112223', '+8801711000011',
             'arif.c@gmail.com', 'O Level', '2025-10-01', 1, 2, 2, 'Partner Agent', 'Active', 'Studying'),
            (12, 'STU-CTG-2025-0002', 'Mst. Rabeya', 'Abdul Gafur', 'Halima Khatun',
             '2003-10-30', 'Female', '1999502222', 'L2223334', '+8801711000012',
             'rabeya@gmail.com', 'HSC', '2025-10-15', 1, 2, 5, 'Partner Agent', 'Active', 'Studying'),
            (13, 'STU-CTG-2025-0003', 'Shovon Das', 'Pranab Das', 'Mina Das',
             '2003-06-05', 'Male', '1999503333', 'M3334445', '+8801711000013',
             'shovon.d@gmail.com', 'A Level', '2025-11-01', 1, 2, None, 'Walk-in', 'Active', 'Studying'),
            (14, 'STU-CTG-2025-0004', 'Fatema Begum', 'Siraj Mia', 'Aleya Begum',
             '2002-01-17', 'Female', '1999504444', 'N4445556', '+8801711000014',
             'fatema.b@gmail.com', 'A Level', '2025-10-01', 2, 2, 2, 'Partner Agent', 'Active', 'Offer Received'),
            (15, 'STU-CTG-2025-0005', 'Kamrul Hasan', 'Mizanur Rahman', 'Shahana Rahman',
             '2002-04-22', 'Male', '1999505555', 'P5556667', '+8801711000015',
             'kamrul.h@gmail.com', 'HSC', '2025-11-01', 2, 2, None, 'Education Fair', 'Active', 'Studying'),
            (16, 'STU-CTG-2025-0006', 'Ruma Begum', 'Nur Hossain', 'Amena Hossain',
             '2000-09-08', 'Female', '1996506666', 'Q6667778', '+8801711000016',
             'ruma.b@gmail.com', 'Bachelor', '2025-10-15', 3, 2, 5, 'Partner Agent', 'Completed', 'Completed'),
            (17, 'STU-DHK-2025-0011', 'Rasel Mia', 'Jalal Mia', 'Sufia Begum',
             '2003-02-14', 'Male', '1999507777', 'R7778889', '+8801711000017',
             'rasel.m@gmail.com', 'HSC', '2025-10-01', 1, 1, None, 'Walk-in', 'Dropped', 'Not Progressing'),
            (18, 'STU-DHK-2025-0012', 'Samiha Rahman', 'Anisur Rahman', 'Lutfun Nahar',
             '2003-08-19', 'Female', '1999508888', 'S8889990', '+8801711000018',
             'samiha.r@gmail.com', 'A Level', '2025-10-01', 2, 1, 1, 'Partner Agent', 'Active', 'Visa Process'),
            (19, 'STU-DHK-2024-0001', 'Adnan Karim', 'Babul Karim', 'Rina Karim',
             '2002-01-10', 'Male', '1998509999', 'T9990001', '+8801711000019',
             'adnan.k@gmail.com', 'A Level', '2024-09-01', 1, 1, None, 'Walk-in', 'Completed', 'Enrolled Abroad'),
            (20, 'STU-CTG-2024-0001', 'Maliha Sultana', 'Zahangir Alam', 'Roksana Alam',
             '2002-05-25', 'Female', '1998500011', 'U0001122', '+8801711000020',
             'maliha.s@gmail.com', 'A Level', '2024-09-01', 2, 2, 2, 'Partner Agent', 'Completed', 'Enrolled Abroad'),
        ]
        for s in students:
            c.execute(
                "INSERT INTO students (student_id, student_code, full_name, father_name, "
                "mother_name, date_of_birth, gender, national_id, passport_no, contact_no, "
                "email, education_qualification, admission_date, programme_id, branch_id, "
                "partner_id, referral_source, status, progression_status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", s
            )
        self.stdout.write(self.style.SUCCESS(f'  {len(students)} students'))

        # ────────────────────────────────────────────────────────
        # 9. STUDENT FEE SETUP
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [9/18] Fee Setups...')
        setup_id = 1
        for s in students:
            sid_s, prog_id, branch_id, adm = s[0], s[13], s[14], s[12]

            total = 250000 if prog_id == 1 else (350000 if prog_id == 2 else 200000)
            inst = 4 if prog_id in (1, 2) else 3
            disc, disc_type, disc_reason = 0, None, None

            if sid_s in (1, 6, 11):
                disc, disc_type, disc_reason = 15000, 'Fixed', 'Early bird discount'
            elif sid_s in (7, 10, 16):
                disc = int(total * 0.10)
                disc_type, disc_reason = 'Percentage', 'Merit scholarship'

            net = total - disc
            c.execute(
                "INSERT INTO student_fee_setup (setup_id, student_id, programme_id, "
                "total_programme_fee, discount_amount, discount_type, discount_reason, "
                "net_payable, currency, installment_count, first_installment_date, "
                "next_interval_days, late_fee_percent, late_fee_max_percent, branch_id) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'BDT',%s,%s,30,2.00,10.00,%s)",
                (setup_id, sid_s, prog_id, total, disc, disc_type, disc_reason, net, inst, adm, branch_id)
            )
            setup_id += 1
        self.stdout.write(self.style.SUCCESS(f'  {setup_id - 1} fee setups'))

        # ────────────────────────────────────────────────────────
        # 10. STUDENT DUES (using COA dict)
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [10/18] Student Dues...')
        due_id = 1

        for s in students:
            sid_s, prog_id, branch_id, adm, status_s = s[0], s[13], s[14], s[12], s[17]

            if prog_id == 1:
                tuition_coa, total = COA['4102'], 250000
            elif prog_id == 2:
                tuition_coa, total = COA['4103'], 350000
            else:
                tuition_coa, total = COA['4104'], 200000

            disc = 0
            if sid_s in (1, 6, 11): disc = 15000
            elif sid_s in (7, 10, 16): disc = int(total * 0.10)

            net = total - disc
            inst = 4 if prog_id in (1, 2) else 3
            inst_amt = round(net / inst)

            # Non-installable fees
            admission_fee = 25000 if prog_id == 1 else (30000 if prog_id == 2 else 20000)
            materials_fee = 10000 if prog_id == 1 else (12000 if prog_id == 2 else 8000)
            non_install = [
                (COA['4101'], admission_fee),
                (COA['4105'], 15000),
                (COA['4106'], 5000),
                (COA['4107'], materials_fee),
            ]
            if prog_id in (1, 2):
                non_install.append((COA['4109'], 10000 if prog_id == 1 else 12000))

            for coa_id, amount in non_install:
                if status_s == 'Dropped':
                    st, paid = 'Waived', 0
                elif sid_s in (7, 10, 16, 19, 20):
                    st, paid = 'Paid', amount
                elif sid_s in (3, 8, 13):
                    st, paid = 'Partial', round(amount * 0.5)
                else:
                    st, paid = 'Paid', amount

                c.execute(
                    "INSERT INTO student_dues (due_id, student_id, coa_id, due_date, "
                    "installment_no, amount, paid_amount, due_amount, status, branch_id) "
                    "VALUES (%s,%s,%s,%s,1,%s,%s,%s,%s,%s)",
                    (due_id, sid_s, coa_id, adm, amount, paid, amount - paid, st, branch_id)
                )
                due_id += 1

            # Tuition installments
            for i in range(inst):
                due_date = str(adm) if i == 0 else str(date.fromisoformat(str(adm)) + timedelta(days=30 * i))

                if status_s == 'Dropped' and i > 0:
                    st, paid = 'Waived', 0
                elif sid_s in (7, 10, 16, 19, 20):
                    st, paid = 'Paid', inst_amt
                elif sid_s in (3, 8, 13):
                    if i < 2: st, paid = 'Paid', inst_amt
                    elif i == 2: st, paid = 'Partial', round(inst_amt * 0.5)
                    else: st, paid = 'Unpaid', 0
                elif i == 0:
                    st, paid = 'Paid', inst_amt
                elif i == 1 and sid_s in (1, 2, 4, 5, 6, 9, 11, 12, 14, 15, 18):
                    st, paid = 'Paid', inst_amt
                else:
                    st = 'Overdue' if date.fromisoformat(due_date) < date.today() else 'Unpaid'
                    paid = 0

                c.execute(
                    "INSERT INTO student_dues (due_id, student_id, coa_id, due_date, "
                    "installment_no, amount, paid_amount, due_amount, status, branch_id) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (due_id, sid_s, tuition_coa, due_date, i + 1, inst_amt, paid, inst_amt - paid, st, branch_id)
                )
                due_id += 1

        self.stdout.write(self.style.SUCCESS(f'  {due_id - 1} due records'))

        # ────────────────────────────────────────────────────────
        # 11. PAYMENTS + PAYMENT ITEMS (using COA dict)
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [11/18] Payments...')
        payment_id = 1
        receipt_no = 1

        payment_data = [
            (1, '2025-10-01', 25000, 'Cash', '', '4101', 'DHK'),
            (1, '2025-10-01', 37500, 'Bank Transfer', 'BANK-001', '4102', 'DHK'),
            (1, '2026-01-15', 37500, 'Bank Transfer', 'BANK-002', '4102', 'DHK'),
            (2, '2025-10-01', 25000, 'Mobile Banking', 'bKash-001', '4101', 'DHK'),
            (2, '2025-10-01', 33750, 'Cash', '', '4102', 'DHK'),
            (2, '2026-01-10', 33750, 'Cash', '', '4102', 'DHK'),
            (3, '2025-10-15', 25000, 'Cash', '', '4101', 'DHK'),
            (3, '2025-10-15', 62500, 'Bank Transfer', 'BANK-003', '4102', 'DHK'),
            (4, '2025-11-01', 25000, 'Mobile Banking', 'Nagad-001', '4101', 'DHK'),
            (4, '2025-11-01', 62500, 'Mobile Banking', 'Nagad-002', '4102', 'DHK'),
            (4, '2026-02-05', 62500, 'Bank Transfer', 'BANK-004', '4102', 'DHK'),
            (5, '2025-11-01', 25000, 'Cash', '', '4101', 'DHK'),
            (5, '2025-11-01', 62500, 'Cash', '', '4102', 'DHK'),
            (6, '2025-10-01', 30000, 'Bank Transfer', 'BANK-005', '4101', 'DHK'),
            (6, '2025-10-01', 52500, 'Bank Transfer', 'BANK-006', '4103', 'DHK'),
            (7, '2025-10-15', 30000, 'Cash', '', '4101', 'DHK'),
            (7, '2025-10-15', 52500, 'Cash', '', '4103', 'DHK'),
            (7, '2026-01-15', 52500, 'Cash', '', '4103', 'DHK'),
            (7, '2026-04-15', 52500, 'Bank Transfer', 'BANK-007', '4103', 'DHK'),
            (8, '2025-11-01', 30000, 'Mobile Banking', 'bKash-003', '4101', 'DHK'),
            (8, '2025-11-01', 52500, 'Mobile Banking', 'bKash-004', '4103', 'DHK'),
            (9, '2025-10-01', 20000, 'Bank Transfer', 'BANK-008', '4101', 'DHK'),
            (9, '2025-10-01', 43333, 'Bank Transfer', 'BANK-009', '4104', 'DHK'),
            (10, '2025-10-15', 20000, 'Cash', '', '4101', 'DHK'),
            (10, '2025-10-15', 43333, 'Cash', '', '4104', 'DHK'),
            (10, '2026-01-15', 43333, 'Cash', '', '4104', 'DHK'),
            (10, '2026-04-15', 43334, 'Cash', '', '4104', 'DHK'),
            (11, '2025-10-01', 25000, 'Cash', '', '4101', 'CTG'),
            (11, '2025-10-01', 58750, 'Bank Transfer', 'BANK-010', '4102', 'CTG'),
            (12, '2025-10-15', 25000, 'Mobile Banking', 'bKash-005', '4101', 'CTG'),
            (12, '2025-10-15', 62500, 'Mobile Banking', 'bKash-006', '4102', 'CTG'),
            (13, '2025-11-01', 25000, 'Cash', '', '4101', 'CTG'),
            (13, '2025-11-01', 62500, 'Cash', '', '4102', 'CTG'),
            (14, '2025-10-01', 30000, 'Cash', '', '4101', 'CTG'),
            (14, '2025-10-01', 87500, 'Bank Transfer', 'BANK-011', '4103', 'CTG'),
            (14, '2026-01-01', 87500, 'Bank Transfer', 'BANK-012', '4103', 'CTG'),
            (15, '2025-11-01', 30000, 'Cash', '', '4101', 'CTG'),
            (15, '2025-11-01', 87500, 'Cash', '', '4103', 'CTG'),
            (16, '2025-10-15', 20000, 'Bank Transfer', 'BANK-013', '4101', 'CTG'),
            (16, '2025-10-15', 43333, 'Bank Transfer', 'BANK-014', '4104', 'CTG'),
            (16, '2026-01-15', 43333, 'Bank Transfer', 'BANK-015', '4104', 'CTG'),
            (16, '2026-04-15', 43334, 'Bank Transfer', 'BANK-016', '4104', 'CTG'),
            (18, '2025-10-01', 30000, 'Cash', '', '4101', 'DHK'),
            (18, '2025-10-01', 87500, 'Bank Transfer', 'BANK-017', '4103', 'DHK'),
            (19, '2024-09-01', 25000, 'Cash', '', '4101', 'DHK'),
            (19, '2024-09-01', 62500, 'Bank Transfer', 'BANK-018', '4102', 'DHK'),
            (19, '2024-12-01', 62500, 'Bank Transfer', 'BANK-019', '4102', 'DHK'),
            (19, '2025-03-01', 62500, 'Bank Transfer', 'BANK-020', '4102', 'DHK'),
            (19, '2025-06-01', 62500, 'Bank Transfer', 'BANK-021', '4102', 'DHK'),
            (20, '2024-09-01', 30000, 'Cash', '', '4101', 'CTG'),
            (20, '2024-09-01', 87500, 'Bank Transfer', 'BANK-022', '4103', 'CTG'),
            (20, '2024-12-01', 87500, 'Bank Transfer', 'BANK-023', '4103', 'CTG'),
            (20, '2025-03-01', 87500, 'Bank Transfer', 'BANK-024', '4103', 'CTG'),
            (20, '2025-06-01', 87500, 'Bank Transfer', 'BANK-025', '4103', 'CTG'),
        ]

        for pd in payment_data:
            s_id, dt, amt, method, ref, coa_code, branch_code = pd
            branch_id = 1 if branch_code == 'DHK' else 2
            receipt = f"MIE-{branch_code}-{dt[:4]}-{receipt_no:04d}"

            c.execute(
                "INSERT INTO payments (payment_id, receipt_no, student_id, date, total_amount, "
                "currency, exchange_rate, amount_in_bdt, payment_method, transaction_ref, "
                "bank_coa_id, collected_by, approved_by, approved_date, status, branch_id) "
                "VALUES (%s,%s,%s,%s,%s,'BDT',1.00,%s,%s,%s,%s,4,2,%s,'Approved',%s)",
                (payment_id, receipt, s_id, dt, amt, amt, method, ref,
                 COA['1121'], dt, branch_id)
            )
            c.execute(
                "INSERT INTO payment_items (payment_id, coa_id, amount) VALUES (%s,%s,%s)",
                (payment_id, COA[coa_code], amt)
            )
            payment_id += 1
            receipt_no += 1

        self.stdout.write(self.style.SUCCESS(f'  {payment_id - 1} payments'))

        # ────────────────────────────────────────────────────────
        # 12. MAIN LEDGER (from payments)
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [12/18] Main Ledger...')
        ledger_id = 1

        c.execute("SELECT payment_id, student_id, date, amount_in_bdt, bank_coa_id, branch_id "
                   "FROM payments WHERE status='Approved'")
        for p_id, s_id, dt, amt, bank_coa, br_id in c.fetchall():
            c.execute("SELECT coa_id FROM payment_items WHERE payment_id=%s", (p_id,))
            item = c.fetchone()
            income_coa = item[0] if item else COA['4101']

            c.execute("SELECT period_id FROM fiscal_periods WHERE %s BETWEEN start_date AND end_date LIMIT 1", (dt,))
            fp = c.fetchone()
            period_id = fp[0] if fp else None

            c.execute(
                "INSERT INTO main_ledger (entry_date, coa_id, description, debit, credit, "
                "reference_type, reference_id, student_id, fiscal_period_id, branch_id) "
                "VALUES (%s,%s,'Payment received',%s,0,'Payment',%s,%s,%s,%s)",
                (dt, bank_coa or COA['1111'], float(amt), p_id, s_id, period_id, br_id)
            )
            ledger_id += 1
            c.execute(
                "INSERT INTO main_ledger (entry_date, coa_id, description, debit, credit, "
                "reference_type, reference_id, student_id, fiscal_period_id, branch_id) "
                "VALUES (%s,%s,'Fee income',0,%s,'Payment',%s,%s,%s,%s)",
                (dt, income_coa, float(amt), p_id, s_id, period_id, br_id)
            )
            ledger_id += 1

        self.stdout.write(self.style.SUCCESS(f'  {ledger_id - 1} ledger entries'))

        # ────────────────────────────────────────────────────────
        # 13. STUDENT LEDGER
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [13/18] Student Ledger...')
        s_ledger_id = 1

        for s in students:
            sid_s, prog_id, branch_id, adm = s[0], s[13], s[14], s[12]
            total = 250000 if prog_id == 1 else (350000 if prog_id == 2 else 200000)

            c.execute(
                "INSERT INTO student_ledger (student_id, entry_date, particulars, "
                "debit, credit, balance, branch_id) VALUES (%s,%s,'Total fee charged',%s,0,%s,%s)",
                (sid_s, adm, total, total, branch_id)
            )
            s_ledger_id += 1

            c.execute("SELECT date, amount_in_bdt FROM payments WHERE student_id=%s AND status='Approved' ORDER BY date", (sid_s,))
            running = total
            for pdate, pamt in c.fetchall():
                running -= float(pamt)
                c.execute(
                    "INSERT INTO student_ledger (student_id, entry_date, particulars, "
                    "debit, credit, balance, branch_id) VALUES (%s,%s,'Payment received',0,%s,%s,%s)",
                    (sid_s, pdate, float(pamt), running, branch_id)
                )
                s_ledger_id += 1

        self.stdout.write(self.style.SUCCESS(f'  {s_ledger_id - 1} student ledger entries'))

        # ────────────────────────────────────────────────────────
        # 14. EXPENSE VOUCHERS (using COA dict)
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [14/18] Expense Vouchers...')
        voucher_id = 1
        v_entry_id = 1

        expenses = [
            ('2025-10-05', 'Staff salaries - October 2025', 'Payment', [
                (COA['5101'], 180000, 0, 1), (COA['5101'], 120000, 0, 2),
                (COA['1121'], 0, 180000, 1), (COA['1121'], 0, 120000, 2),
            ]),
            ('2025-10-10', 'Office rent - October 2025', 'Payment', [
                (COA['5201'], 65000, 0, 1), (COA['5201'], 45000, 0, 2),
                (COA['1121'], 0, 65000, 1), (COA['1121'], 0, 45000, 2),
            ]),
            ('2025-10-15', 'NCUK annual registration fee', 'Payment', [
                (COA['5501'], 250000, 0, 1), (COA['1123'], 0, 1608, 1),
            ]),
            ('2025-10-20', 'Marketing - Facebook ads + flyers', 'Payment', [
                (COA['5401'], 35000, 0, 1), (COA['5405'], 15000, 0, 1),
                (COA['1111'], 0, 50000, 1),
            ]),
            ('2025-11-05', 'Staff salaries - November 2025', 'Payment', [
                (COA['5101'], 180000, 0, 1), (COA['5101'], 120000, 0, 2),
                (COA['1121'], 0, 180000, 1), (COA['1121'], 0, 120000, 2),
            ]),
            ('2025-11-10', 'Office rent - November 2025', 'Payment', [
                (COA['5201'], 65000, 0, 1), (COA['5201'], 45000, 0, 2),
                (COA['1121'], 0, 65000, 1), (COA['1121'], 0, 45000, 2),
            ]),
            ('2025-12-05', 'Staff salaries - December 2025', 'Payment', [
                (COA['5101'], 180000, 0, 1), (COA['5101'], 120000, 0, 2),
                (COA['1121'], 0, 180000, 1), (COA['1121'], 0, 120000, 2),
            ]),
            ('2025-12-10', 'Office rent - December 2025', 'Payment', [
                (COA['5201'], 65000, 0, 1), (COA['5201'], 45000, 0, 2),
                (COA['1121'], 0, 65000, 1), (COA['1121'], 0, 45000, 2),
            ]),
            ('2026-01-05', 'Staff salaries - January 2026', 'Payment', [
                (COA['5101'], 190000, 0, 1), (COA['5101'], 125000, 0, 2),
                (COA['1121'], 0, 190000, 1), (COA['1121'], 0, 125000, 2),
            ]),
            ('2026-01-10', 'Office rent - January 2026', 'Payment', [
                (COA['5201'], 65000, 0, 1), (COA['5201'], 45000, 0, 2),
                (COA['1121'], 0, 65000, 1), (COA['1121'], 0, 45000, 2),
            ]),
            ('2026-01-20', 'Teaching materials purchase', 'Payment', [
                (COA['5503'], 28000, 0, 1), (COA['5503'], 18000, 0, 2),
                (COA['1111'], 0, 46000, 1),
            ]),
            ('2026-02-05', 'Staff salaries - February 2026', 'Payment', [
                (COA['5101'], 190000, 0, 1), (COA['5101'], 125000, 0, 2),
                (COA['1121'], 0, 190000, 1), (COA['1121'], 0, 125000, 2),
            ]),
            ('2026-03-05', 'Staff salaries - March 2026', 'Payment', [
                (COA['5101'], 190000, 0, 1), (COA['5101'], 125000, 0, 2),
                (COA['1121'], 0, 190000, 1), (COA['1121'], 0, 125000, 2),
            ]),
            ('2026-03-15', 'Education fair setup and materials', 'Payment', [
                (COA['5402'], 45000, 0, 1), (COA['5405'], 20000, 0, 1),
                (COA['1111'], 0, 65000, 1),
            ]),
            ('2026-04-05', 'Staff salaries - April 2026', 'Payment', [
                (COA['5101'], 190000, 0, 1), (COA['5101'], 125000, 0, 2),
                (COA['1121'], 0, 190000, 1), (COA['1121'], 0, 125000, 2),
            ]),
            ('2026-05-05', 'Staff salaries - May 2026', 'Payment', [
                (COA['5101'], 190000, 0, 1), (COA['5101'], 125000, 0, 2),
                (COA['1121'], 0, 190000, 1), (COA['1121'], 0, 125000, 2),
            ]),
            ('2026-05-15', 'Internet + phone bills', 'Payment', [
                (COA['5301'], 8000, 0, 1), (COA['5302'], 5000, 0, 1),
                (COA['5301'], 6000, 0, 2), (COA['5302'], 3000, 0, 2),
                (COA['1111'], 0, 22000, 1),
            ]),
            ('2026-06-05', 'Staff salaries - June 2026', 'Payment', [
                (COA['5101'], 190000, 0, 1), (COA['5101'], 125000, 0, 2),
                (COA['1121'], 0, 190000, 1), (COA['1121'], 0, 125000, 2),
            ]),
        ]

        for dt, narr, vtype, entries in expenses:
            total_dr = sum(e[1] for e in entries)
            total_cr = sum(e[2] for e in entries)
            vno = f"MIE-VOU-{dt[:4]}-{voucher_id:04d}"

            c.execute(
                "INSERT INTO vouchers (voucher_id, voucher_no, voucher_type, date, narration, "
                "total_debit, total_credit, prepared_by, approved_by, approved_date, "
                "status, branch_id) VALUES (%s,%s,%s,%s,%s,%s,%s,4,2,%s,'Approved',1)",
                (voucher_id, vno, vtype, dt, narr, total_dr, total_cr, dt)
            )

            c.execute("SELECT period_id FROM fiscal_periods WHERE %s BETWEEN start_date AND end_date LIMIT 1", (dt,))
            fp = c.fetchone()
            period_id = fp[0] if fp else None

            line = 1
            for coa_id, dr, cr, br in entries:
                c.execute(
                    "INSERT INTO voucher_entries (entry_id, voucher_id, line_number, coa_id, "
                    "debit, credit, narration) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (v_entry_id, voucher_id, line, coa_id, dr, cr, narr)
                )
                c.execute(
                    "INSERT INTO main_ledger (entry_date, coa_id, description, "
                    "debit, credit, reference_type, reference_id, voucher_id, "
                    "voucher_entry_id, fiscal_period_id, branch_id) "
                    "VALUES (%s,%s,%s,%s,%s,'Voucher',%s,%s,%s,%s,%s)",
                    (dt, coa_id, narr, dr, cr, voucher_id, voucher_id, v_entry_id, period_id, br)
                )
                ledger_id += 1
                v_entry_id += 1
                line += 1

            voucher_id += 1

        self.stdout.write(self.style.SUCCESS(f'  {voucher_id - 1} vouchers, {v_entry_id - 1} entries'))

        # ────────────────────────────────────────────────────────
        # 15. PETTY CASH
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [15/18] Petty Cash...')
        petty = [
            (1, '2025-10-03', 'Office stationery', 'Office Supplies', 1200, 'Rafiq', 1),
            (2, '2025-10-08', 'Courier to NCUK office', 'Courier', 500, 'Office Boy', 1),
            (3, '2025-10-15', 'Tea for staff meeting', 'Refreshment', 800, 'Office Boy', 1),
            (4, '2025-10-22', 'Taxi - student docs', 'Transport', 350, 'Rafiq', 1),
            (5, '2025-11-05', 'Printer toner', 'Office Supplies', 2500, 'Rafiq', 1),
            (6, '2025-11-12', 'Cleaning supplies', 'Cleaning', 1500, 'Office Boy', 1),
            (7, '2025-11-20', 'Courier to student', 'Courier', 300, 'Nadia', 1),
            (8, '2025-12-03', 'Office supplies', 'Office Supplies', 1800, 'Rafiq', 1),
            (9, '2025-12-10', 'Guest lecturer refreshments', 'Refreshment', 1200, 'Office Boy', 1),
            (10, '2026-01-05', 'Office decoration', 'Miscellaneous', 3000, 'Office Boy', 1),
            (11, '2026-01-15', 'Courier to university', 'Courier', 600, 'Rafiq', 1),
            (12, '2026-02-05', 'Office supplies', 'Office Supplies', 1400, 'Rafiq', 1),
            (13, '2026-03-10', 'Whiteboard markers', 'Office Supplies', 900, 'Nadia', 1),
            (14, '2026-04-05', 'Water filter service', 'Repair', 2000, 'Office Boy', 1),
            (15, '2026-05-10', 'AC servicing', 'Repair', 3500, 'Office Boy', 1),
            (16, '2025-10-05', 'Stationery CTG', 'Office Supplies', 1000, 'Bablu', 2),
            (17, '2025-10-20', 'Courier CTG', 'Courier', 400, 'Office Boy', 2),
            (18, '2025-11-10', 'Cleaning CTG', 'Cleaning', 1200, 'Office Boy', 2),
            (19, '2026-01-10', 'Supplies CTG', 'Office Supplies', 1500, 'Bablu', 2),
            (20, '2026-03-15', 'Chair repair CTG', 'Repair', 1800, 'Office Boy', 2),
        ]
        for pc in petty:
            c.execute(
                "INSERT INTO petty_cash (cash_id, date, purpose, category, amount, "
                "given_to, approved_by, branch_id, created_by) VALUES (%s,%s,%s,%s,%s,%s,2,%s,4)", pc
            )
        self.stdout.write(self.style.SUCCESS(f'  {len(petty)} petty cash'))

        # ────────────────────────────────────────────────────────
        # 16. ACADEMIC RECORDS + ATTENDANCE
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [16/18] Academics...')
        modules = {
            1: [('Mathematics for Engineers', 'MAT101'), ('Physics', 'PHY101'),
                ('English for Academic Purposes', 'ENG101'), ('ICT', 'ICT101'),
                ('Study Skills', 'SSK101')],
            2: [('Advanced Mathematics', 'MAT201'), ('Engineering Principles', 'ENG201'),
                ('Academic English', 'ENG202'), ('Computer Science Fundamentals', 'CS201'),
                ('Business Studies', 'BUS201'), ('Research Methods', 'RES201')],
            3: [('Research Methodology', 'RES301'), ('Academic Writing', 'AWR301'),
                ('Critical Thinking', 'CTH301'), ('Subject Specific Module', 'SSM301')],
        }
        grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
        record_id = 1

        for s in students:
            sid_s, prog_id, branch_id = s[0], s[13], s[14]
            if s[17] == 'Dropped':
                continue
            for mname, mcode in modules.get(prog_id, []):
                for atype in ['Coursework', 'Exam']:
                    score = random.randint(45, 95)
                    grade_idx = min(score // 12, 6)
                    result = 'Distinction' if score >= 70 else ('Pass' if score >= 40 else 'Fail')
                    c.execute(
                        "INSERT INTO academic_records (record_id, student_id, programme_id, "
                        "module_name, module_code, assessment_type, score, grade, max_score, "
                        "result, assessment_date, academic_year_id, recorded_by, branch_id) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,100,%s,%s,1,6,%s)",
                        (record_id, sid_s, prog_id, mname, mcode, atype,
                         score, grades[grade_idx], result,
                         '2026-01-15' if atype == 'Coursework' else '2026-03-15', branch_id)
                    )
                    record_id += 1

        att_id = 1
        for s in students:
            sid_s, prog_id, branch_id = s[0], s[13], s[14]
            if s[17] == 'Dropped':
                continue
            for day_offset in range(0, 120, 3):
                att_date = date(2025, 10, 1) + timedelta(days=day_offset)
                if att_date > date.today():
                    break
                st = random.choices(['Present', 'Absent', 'Late'], weights=[80, 10, 10])[0]
                c.execute(
                    "INSERT INTO attendance (student_id, programme_id, attendance_date, "
                    "session_type, status, recorded_by, branch_id) "
                    "VALUES (%s,%s,%s,'Lecture',%s,6,%s)",
                    (sid_s, prog_id, att_date, st, branch_id)
                )
                att_id += 1

        self.stdout.write(self.style.SUCCESS(f'  {record_id - 1} records, {att_id - 1} attendance'))

        # ────────────────────────────────────────────────────────
        # 17. DISCOUNTS + DOCUMENTS
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [17/18] Discounts & Documents...')
        discounts = [
            (1, 1, 'Early Bird', 'Fixed Amount', 15000, 'All Fees', 15000,
             'Early enrollment discount', 2, '2025-10-01', 1),
            (2, 6, 'Early Bird', 'Fixed Amount', 15000, 'All Fees', 15000,
             'Early enrollment discount', 2, '2025-10-01', 1),
            (3, 7, 'Merit Scholarship', 'Percentage', 10, 'All Fees', 35000,
             'Outstanding A-Level results: 3A*', 2, '2025-10-15', 1),
            (4, 10, 'Merit Scholarship', 'Percentage', 10, 'All Fees', 20000,
             'Excellent Bachelor: CGPA 3.8', 2, '2025-10-15', 1),
            (5, 11, 'Early Bird', 'Fixed Amount', 15000, 'All Fees', 15000,
             'Early enrollment CTG', 7, '2025-10-01', 2),
            (6, 16, 'Merit Scholarship', 'Percentage', 10, 'All Fees', 20000,
             'First class honours', 7, '2025-10-15', 2),
        ]
        for d in discounts:
            c.execute(
                "INSERT INTO discounts (discount_id, student_id, discount_type, discount_basis, "
                "discount_value, applicable_to, calculated_amount, reason, "
                "approved_by, approval_date, branch_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", d
            )

        docs = [
            (1, 'Passport', 'sakib_passport.pdf', 1), (1, 'Transcript', 'sakib_transcript.pdf', 1),
            (2, 'National ID', 'tania_nid.pdf', 1), (2, 'Transcript', 'tania_transcript.pdf', 1),
            (3, 'Passport', 'rafiq_passport.pdf', 1), (3, 'IELTS/English', 'rafiq_ielts.pdf', 1),
            (6, 'Passport', 'nusrat_passport.pdf', 1), (6, 'Certificate', 'nusrat_certificate.pdf', 1),
            (7, 'Passport', 'tanvir_passport.pdf', 1), (7, 'Offer Letter', 'tanvir_offer.pdf', 1),
            (11, 'Passport', 'arif_passport.pdf', 2), (11, 'Transcript', 'arif_transcript.pdf', 2),
            (14, 'Passport', 'fatema_passport.pdf', 2), (14, 'Offer Letter', 'fatema_offer.pdf', 2),
            (19, 'Passport', 'adnan_passport.pdf', 1), (19, 'Visa Copy', 'adnan_visa.pdf', 1),
            (20, 'Passport', 'maliha_passport.pdf', 2), (20, 'Visa Copy', 'maliha_visa.pdf', 2),
        ]
        for i, (sid_s, dtype, fname, br) in enumerate(docs, 1):
            c.execute(
                "INSERT INTO student_documents (doc_id, student_id, document_type, file_name, "
                "file_path, is_verified, branch_id, uploaded_by) "
                "VALUES (%s,%s,%s,%s,%s,1,%s,4)",
                (i, sid_s, dtype, fname, f'/docs/{sid_s}/{fname}', br)
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(discounts)} discounts, {len(docs)} docs'))

        # ────────────────────────────────────────────────────────
        # 18. PROGRESSION & COMMISSIONS
        # ────────────────────────────────────────────────────────
        self.stdout.write('  [18/18] Progression & Commissions...')

        progressions = [
            (1, 5, 1, 'BSc Computer Science', 'UK', '2026-03-01', 'Offer Accepted',
             '2026-04-15', 'Unconditional', 18000, 'GBP', 'Applied', None, 'Not Enrolled', None, 'Pending', 1),
            (2, 7, 2, 'BEng Mechanical Engineering', 'UK', '2026-02-01', 'Offer Accepted',
             '2026-03-10', 'Unconditional', 22000, 'GBP', 'Granted', '2026-05-20', 'Enrolled', '2026-06-01', 'Pending', 1),
            (3, 10, 3, 'MSc Data Science', 'UK', '2026-03-15', 'Offer Accepted',
             '2026-04-20', 'Unconditional', 25000, 'GBP', 'Granted', '2026-05-25', 'Enrolled', '2026-06-05', 'Pending', 1),
            (4, 14, 4, 'BSc Business Management', 'UK', '2026-04-01', 'Conditional Offer',
             None, 'Conditional', 16000, 'GBP', 'Not Started', None, 'Not Enrolled', None, 'Not Applicable', 2),
            (5, 16, 5, 'MBA', 'UK', '2026-02-15', 'Offer Accepted',
             '2026-03-20', 'Unconditional', 20000, 'GBP', 'Granted', '2026-05-10', 'Enrolled', '2026-06-01', 'Pending', 2),
            (6, 19, 1, 'BSc Computer Science', 'UK', '2025-04-01', 'Offer Accepted',
             '2025-05-15', 'Unconditional', 18000, 'GBP', 'Granted', '2025-07-20', 'Enrolled', '2025-09-15', 'Received', 1),
            (7, 20, 2, 'BEng Civil Engineering', 'UK', '2025-04-15', 'Offer Accepted',
             '2025-05-20', 'Unconditional', 22000, 'GBP', 'Granted', '2025-07-25', 'Enrolled', '2025-09-15', 'Received', 2),
            (8, 18, 3, 'BSc Business Analytics', 'UK', '2026-05-01', 'Offer Accepted',
             '2026-05-20', 'Unconditional', 21000, 'GBP', 'Applied', None, 'Not Enrolled', None, 'Pending', 1),
        ]
        for p in progressions:
            c.execute(
                "INSERT INTO progression_records (record_id, student_id, university_id, "
                "programme_applied, country, application_date, application_status, "
                "offer_date, offer_type, tuition_fee_at_uni, tuition_currency, "
                "visa_status, visa_grant_date, enrollment_status, enrollment_date, "
                "commission_status, branch_id, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,4)", p
            )

        uni_comm = [
            (1, 6, 1, 19, 'Percentage of Tuition', 15.00, 18000, 2700, 'GBP', 158.00, 426600, 'Received', 1),
            (2, 7, 2, 20, 'Percentage of Tuition', 12.50, 22000, 2750, 'GBP', 158.00, 434500, 'Received', 2),
            (3, 2, 2, 7, 'Percentage of Tuition', 12.50, 22000, 2750, 'GBP', 158.00, 434500, 'Expected', 1),
            (4, 3, 3, 10, 'Percentage of Tuition', 10.00, 25000, 2500, 'GBP', 158.00, 395000, 'Expected', 1),
            (5, 5, 5, 16, 'Percentage of Tuition', 12.00, 20000, 2400, 'GBP', 158.00, 379200, 'Expected', 2),
        ]
        for uc in uni_comm:
            c.execute(
                "INSERT INTO university_commissions (commission_id, progression_record_id, "
                "university_id, student_id, commission_type, commission_rate, tuition_base, "
                "gross_commission, commission_currency, exchange_rate, commission_in_bdt, "
                "status, branch_id, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,4)", uc
            )

        partner_comm = [
            (1, 4, 7, 3, 'Fixed Per Student', None, 434500, 25000, 'Approved', 25000, 1),
            (2, 2, 20, 2, 'Percentage of University Commission', 12.50, 434500, 54312, 'Paid', 0, 2),
            (3, 3, 10, 4, 'Percentage of MIE Fee', 10.00, 200000, 20000, 'Calculated', 20000, 1),
            (4, 5, 16, 5, 'Percentage of University Commission', 10.00, 379200, 37920, 'Calculated', 37920, 2),
        ]
        for pc in partner_comm:
            c.execute(
                "INSERT INTO partner_commissions (partner_commission_id, partner_id, student_id, "
                "university_commission_id, commission_type, commission_rate, base_amount, "
                "calculated_amount, calculated_date, status, remaining_amount, "
                "branch_id, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'2026-06-01',%s,%s,%s,4)", pc
            )

        c.execute(
            "INSERT INTO partner_payments (partner_payment_id, partner_commission_id, "
            "partner_id, payment_date, amount, payment_method, transaction_ref, "
            "bank_coa_id, status, branch_id, created_by, approved_by) "
            "VALUES (1,2,2,'2026-06-05',54312,'Bank Transfer','BANK-PP-001',%s,'Completed',2,4,2)",
            (COA['1121'],)
        )

        # Update student financial totals
        c.execute("""
            UPDATE students s SET
                total_fee = COALESCE((SELECT SUM(amount) FROM student_dues WHERE student_id = s.student_id), 0),
                total_paid = COALESCE((SELECT SUM(paid_amount) FROM student_dues WHERE student_id = s.student_id), 0),
                total_due = COALESCE((SELECT SUM(due_amount) FROM student_dues WHERE student_id = s.student_id), 0)
        """)

        self.stdout.write(self.style.SUCCESS(
            f'  {len(progressions)} progressions, {len(uni_comm)} commissions, {len(partner_comm)} partner payouts'
        ))

        # ────────────────────────────────────────────────────────
        # DONE
        # ────────────────────────────────────────────────────────
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('  ALL TABLES SEEDED SUCCESSFULLY'))
        self.stdout.write(self.style.SUCCESS(f'  {len(students)} students'))
        self.stdout.write(self.style.SUCCESS(f'  {payment_id - 1} payments'))
        self.stdout.write(self.style.SUCCESS(f'  {ledger_id - 1} ledger entries'))
        self.stdout.write(self.style.SUCCESS(f'  {voucher_id - 1} vouchers'))
        self.stdout.write(self.style.SUCCESS(f'  {due_id - 1} due records'))
        self.stdout.write(self.style.SUCCESS(f'  {len(progressions)} progressions'))
        self.stdout.write(self.style.WARNING('=' * 60))
