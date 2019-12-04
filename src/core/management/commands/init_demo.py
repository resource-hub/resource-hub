from django.core.management.base import BaseCommand, CommandError

import core.tests.demodb as demodb


class Command(BaseCommand):
    help = 'Tool for initiazling demo data on the plattform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            action='store_true',
            help='Create demo users',
        )

        parser.add_argument(
            '--organizations',
            action='store_true',
            help='Create demo organizations (needs existing users)',
        )

        parser.add_argument(
            '--full',
            action='store_true',
            help='Create complete demo database',
        )

    def handle(self, *args, **options):
        if options['users']:
            demodb.create_users()

        if options['organizations']:
            demodb.create_organizations()

        if options['full']:
            demodb.create_users()
            demodb.create_organizations()
            self.stdout.write(self.style.SUCCESS('Demo database initialized'))
