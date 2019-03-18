from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from datetime import datetime, timedelta
import tempfile

from observe.images import check_request_api, make_timelapse, find_frames_object, download_frames
from observe.models import Asteroid

class Command(BaseCommand):
    help = 'Update pending blocks if observation requests have been made'

    def handle(self, *args, **options):
        self.stdout.write("==== Updating Asteroids %s  ====" % (datetime.now().strftime('%Y-%m-%d %H:%M')))
        tmp_dir = settings.MEDIA_ROOT
        for ast in Asteroid.objects.filter(active=True):
            num_images = 5
            frames, last_update = find_frames_object(ast)
            tmpdir = tempfile.mkdtemp()
            confirm = download_frames(ast.text_name(), frames, download_dir=tmpdir)
            outfile_mp4 = make_timelapse(ast, tmpdir)
            ast.last_update = last_update
            outfile_webm = make_timelapse(ast, tmpdir, format='webm')
            ast.save()
