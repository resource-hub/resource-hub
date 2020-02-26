
from django.core.management.base import BaseCommand, CommandError

from resource_hub.core.jobs import clear_schedule, init_schedule


class Command(BaseCommand):
    help = 'Tool for initiazling demo data on the plattform'

    def handle(self, *args, **options):
        clear_schedule()
        init_schedule()
        self.stdout.write(self.style.SUCCESS('Schedule initialized'))
