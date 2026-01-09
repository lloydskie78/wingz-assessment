from django.core.management.base import BaseCommand
from rides.models import User


class Command(BaseCommand):
    help = 'Create an admin user with role="admin"'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email address for the admin user')
        parser.add_argument('--password', type=str, required=True, help='Password for the admin user')
        parser.add_argument('--first-name', type=str, default='Admin', help='First name (default: Admin)')
        parser.add_argument('--last-name', type=str, default='User', help='Last name (default: User)')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'User with email {email} already exists.'))
            return

        user = User.objects.create_user(
            email=email,
            password=password,
            role='admin',
            first_name=first_name,
            last_name=last_name
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {email}'))

