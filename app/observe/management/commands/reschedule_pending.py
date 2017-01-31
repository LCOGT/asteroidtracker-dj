from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from datetime import datetime, timedelta
from observe.images import check_request_api
from observe.schedule import get_headers
from observe.views import state_options, send_request
from observe.models import Asteroid, Observation

class Command(BaseCommand):
    help = 'Update pending blocks if observation requests have been made'

    def handle(self, *args, **options):
        pending = Observation.objects.filter(status='P')
        self.stdout.write("==== Updating %s Pending %s  ====" % (pending.count(), datetime.now().strftime('%Y-%m-%d %H:%M')))
        reschedule = []
        headers = get_headers(url = 'https://lcogt.net/observe/api/api-token-auth/')
        for obs in pending:
            status = check_request_api(obs.track_num, headers)
            state = state_options.get(status['state'],'U')
            obs.status = state
            obs.save()
            if state in ('F','U'):
                item = {'user_name' : obs.email}
                resp = send_request(obs.asteroid, item)
                self.stdout.write(resp['msg'])
