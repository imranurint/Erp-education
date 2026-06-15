from django.core.management.base import BaseCommand
from apps.core.models import User, Branch


class Command(BaseCommand):
    help = 'Create initial super admin user'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True)
        parser.add_argument('--email', type=str, required=True)
        parser.add_argument('--password', type=str, required=True)

    def handle(self, *args, **options):
        name = options['name']
        email = options['email']
        password = options['password']

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'User {email} already exists'))
            return

        user = User.objects.create_superuser(
            name=name,
            email=email,
            password=password,
            role='Super Admin',
            is_staff=True,
            is_superuser=True,
        )

        self.stdout.write(self.style.SUCCESS(
            f'Super Admin created: {user.name} ({user.email})'
        ))
