from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from datetime import datetime, timedelta
from observe.views import update_status
from observe.images import check_request_api, make_timelapse, find_frames_object, download_frames
from observe.models import Observation, Asteroid

class Command(BaseCommand):
    help = 'Update pending blocks if observation requests have been made'

    def handle(self, *args, **options):
        requests = Observation.objects.filter(~Q(status='C')|~Q(status='F'))
        self.stdout.write("==== %s Pending requests %s ====" % (requests.count(), datetime.now().strftime('%Y-%m-%d %H:%M')))
        for req in requests:
            self.stdout.write("Updating {}".format(req))
            frames = update_status(req)
