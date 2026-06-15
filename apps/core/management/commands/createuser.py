from django.core.management.base import BaseCommand
from apps.core.models import User, Branch


class Command(BaseCommand):
    help = 'Create a new user with role and branch'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True)
        parser.add_argument('--email', type=str, required=True)
        parser.add_argument('--password', type=str, required=True)
        parser.add_argument('--role', type=str, required=True, choices=[
            'Super Admin', 'Branch Admin', 'Accountant',
            'Collector', 'Counselor', 'Academic'
        ])
        parser.add_argument('--branch', type=str, help='Branch code: DHK or CTG')

    def handle(self, *args, **options):
        name = options['name']
        email = options['email']
        password = options['password']
        role = options['role']
        branch_code = options.get('branch')

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'User {email} already exists'))
            return

        branch = None
        if branch_code:
            try:
                branch = Branch.objects.get(branch_code=branch_code)
            except Branch.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f'Branch {branch_code} not found. Use DHK or CTG'
                ))
                return

        user = User.objects.create_user(
            name=name,
            email=email,
            password=password,
            role=role,
            branch=branch,
        )

        self.stdout.write(self.style.SUCCESS(
            f'User created: {user.name} | {user.role} | {user.email}'
        ))
