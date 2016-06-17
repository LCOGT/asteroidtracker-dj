from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from datetime import datetime, timedelta
from observe.images import check_request_api, make_timelapse, find_frames_object, download_frames
from observe.models importAsteroid

class Command(BaseCommand):
    help = 'Update pending blocks if observation requests have been made'

    def handle(self, *args, **options):
        self.stdout.write("==== Updating Asteroids %s  ====" % (datetime.now().strftime('%Y-%m-%d %H:%M')))
        for ast in Asteroid.objects.filter(active=True):
            frames, last_update = find_frames_object(ast)
            confirm = download_frames(ast.text_name(), frames, download_dir=settings.MEDIA_ROOT)
            num_images = make_timelapse(ast)
            ast.num_observations += num_images
            ast.last_update = last_update
            ast.save()
