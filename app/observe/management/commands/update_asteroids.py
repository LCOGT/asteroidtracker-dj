from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from datetime import datetime, timedelta
import tempfile
import shutil

from observe.images import timelapse_overseer
from observe.models import Asteroid

class Command(BaseCommand):
    help = 'Update pending blocks if observation requests have been made'

    def handle(self, *args, **options):
        self.stdout.write("==== Updating Asteroids %s  ====" % (datetime.now().strftime('%Y-%m-%d %H:%M')))

        for ast in Asteroid.objects.filter(active=True):
            num_images = 5
            tmpdir = tempfile.mkdtemp()
            timelapse_overseer(ast_id=ast.id, dir=tmpdir)
            if not settings.DEBUG:
                shutil.rmtree(tmpdir)
