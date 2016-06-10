from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from datetime import datetime, timedelta
from observe.views import update_status
from observe.models import Request, Asteroid

class Command(BaseCommand):
    help = 'Update pending blocks if observation requests have been made'

    def handle(self, *args, **options):
        requests = Request.objects.filter(~Q(status='C'))
        self.stdout.write("==== %s Pending Requests %s ====" % (requests.count(), datetime.now().strftime('%Y-%m-%d %H:%M')))
        for req in requests:
            frames = update_status(req)
