from django.core.management.base import BaseCommand
from apps.core.models import User, Branch


class Command(BaseCommand):
    help = 'Seed all demo users for testing'

    def handle(self, *args, **options):
        dhk = Branch.objects.get(branch_code='DHK')
        ctg = Branch.objects.get(branch_code='CTG')

        users_data = [
            # ── SUPER ADMIN ──────────────────────
            {
                'name': 'Amran Hossain',
                'email': 'amran@miepathways.com',
                'password': 'MIE@2026!',
                'role': 'Super Admin',
                'branch': None,
                'is_superuser': True,
                'is_staff': True,
            },

            # ── DHAKA BRANCH ─────────────────────
            {
                'name': 'Fatima Rahman',
                'email': 'fatima@miepathways.com',
                'password': 'MIE@2026!',
                'role': 'Branch Admin',
                'branch': dhk,
            },
            {
                'name': 'Karim Ahmed',
                'email': 'karim@miepathways.com',
                'password': 'MIE@2026!',
                'role': 'Accountant',
                'branch': dhk,
            },
            {
                'name': 'Rafiq Collector',
                'email': 'rafiq@miepathways.com',
                'password': 'MIE@2026!',
                'role': 'Collector',
                'branch': dhk,
            },
            {
                'name': 'Nadia Counselor',
                'email': 'nadia@miepathways.com',
                'password': 'MIE@2026!',
                'role': 'Counselor',
                'branch': dhk,
            },

            # ── CHATTOGRAM BRANCH ────────────────
            {
                'name': 'Zahir Chowdhury',
                'email': 'zahir@miepathways.com',
                'password': 'MIE@2026!',
                'role': 'Branch Admin',
                'branch': ctg,
            },
            {
                'name': 'Sumon Das',
                'email': 'sumon@miepathways.com',
                'password': 'MIE@2026!',
                'role': 'Accountant',
                'branch': ctg,
            },
            {
                'name': 'Bablu Collector',
                'email': 'bablu@miepathways.com',
                'password': 'MIE@2026!',
                'role': 'Collector',
                'branch': ctg,
            },
        ]

        created_count = 0
        for data in users_data:
            is_superuser = data.pop('is_superuser', False)
            is_staff = data.pop('is_staff', False)
            password = data.pop('password')

            if User.objects.filter(email=data['email']).exists():
                self.stdout.write(self.style.WARNING(f'  Skip: {data["email"]} (exists)'))
                continue

            user = User(**data)
            user.set_password(password)
            user.is_superuser = is_superuser
            user.is_staff = is_staff
            user.save()
            created_count += 1
            self.stdout.write(self.style.SUCCESS(
                f'  Created: {user.email} | {user.role} | {user.branch or "All Branches"}'
            ))

        self.stdout.write(self.style.SUCCESS(f'\nTotal created: {created_count}'))
