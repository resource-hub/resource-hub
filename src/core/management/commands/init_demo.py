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
            testdb.create_users()

        if options['organizations']:
            testdb.create_organizations()

        if options['full']:
            testdb.create_users()
            testdb.create_organizations()
            self.stdout.write(self.style.SUCCESS('Demo database initialized'))
